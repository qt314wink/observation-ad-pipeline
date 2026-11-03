"""Hosted native-media and capture-provenance regression using a generated tone."""
import json
import math
import os
from pathlib import Path
import signal
import struct
import subprocess
import tempfile
import time
import urllib.request
import wave

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
URL = 'http://127.0.0.1:8765/integrations/audio-reactive/'
OUT = ROOT / 'audio-reactive-evidence'

def tone(path):
    rate=24000
    with wave.open(str(path),'wb') as out:
        out.setnchannels(1); out.setsampwidth(2); out.setframerate(rate)
        out.writeframes(b''.join(struct.pack('<h',int(9000*math.sin(2*math.pi*220*i/rate))) for i in range(rate*8)))

def wait_packets(page, minimum):
    page.wait_for_function(r'''n => {
      const match=document.querySelector('#stats').textContent.match(/captured packets (\d+)/);
      return match && Number(match[1]) >= n;
    }''', arg=minimum, timeout=20000)

def main():
    server=subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    try:
        for _ in range(80):
            try:
                with urllib.request.urlopen(URL,timeout=1) as response:
                    if response.status==200: break
            except OSError: time.sleep(.1)
        else: raise RuntimeError('test server did not start')
        with tempfile.TemporaryDirectory() as temp, sync_playwright() as p:
            fixture=Path(temp)/'generated-tone.wav'; tone(fixture)
            browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE'),args=['--autoplay-policy=no-user-gesture-required'])
            page=browser.new_page(); errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(URL,wait_until='domcontentloaded')
            page.locator('#file').set_input_files(str(fixture))
            page.locator('#player').evaluate('el => el.play()')
            expect(page.locator('#state')).to_have_text('Playing local audio.')
            wait_packets(page,4)
            page.wait_for_function("Number(document.querySelector('#stats').textContent.match(/RMS ([0-9.]+)/)?.[1]) > 0.01",timeout=20000)
            page.locator('#sensitivity').evaluate("el => { el.value='22'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
            wait_packets(page,14)
            page.locator('#player').evaluate('el => el.pause()')
            expect(page.locator('#state')).to_contain_text('Audio paused')
            page.locator('#sensitivity').evaluate("el => { el.value='30'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
            OUT.mkdir(exist_ok=True)
            with page.expect_download() as event: page.locator('#export').click()
            target=OUT/'native-tone-capture.json';event.value.save_as(target)
            capture=json.loads(target.read_text())
            assert capture['format']=='audio-reactive-capture.v0.2'
            assert capture['source']=='local-audio-file' and capture['source_media_included'] is False
            assert [s['config']['sensitivity'] for s in capture['config_segments']]==[14,22]
            assert capture['config_segments'][0]['start_packet']==0
            assert capture['config_segments'][-1]['end_packet_exclusive']==len(capture['packets'])
            assert max(x['controls']['energy'] for x in capture['packets'])>0
            assert 'generated-tone.wav' not in target.read_text()
            page.locator('#player').evaluate('el => el.play()')
            expect(page.locator('#state')).to_have_text('Playing local audio.')
            wait_packets(page,len(capture['packets'])+3)
            page.locator('#stop').click()
            expect(page.locator('#state')).to_contain_text('remain available')
            with page.expect_download() as event: page.locator('#export').click()
            stopped=OUT/'stopped-tone-capture.json';event.value.save_as(stopped)
            stopped_capture=json.loads(stopped.read_text())
            assert stopped_capture['source']=='local-audio-file'
            assert len(stopped_capture['packets'])>=len(capture['packets'])+3
            page.locator('#demo').click()
            expect(page.locator('#mode')).to_contain_text('Synthetic signal')
            page.locator('#player').evaluate('el => el.play()')
            expect(page.locator('#state')).to_have_text('Playing local audio.')
            expect(page.locator('#mode')).to_have_text('Local file')
            assert not errors,errors
            broken=browser.new_page()
            broken.add_init_script('''window.AudioContext=class {
              constructor(){this.state='running';this.sampleRate=48000;this.destination={};}
              createAnalyser(){return {frequencyBinCount:1024,connect(){}};}
              createMediaElementSource(){throw new Error('synthetic graph failure');}
            };''')
            broken.goto(URL,wait_until='domcontentloaded')
            broken.locator('#file').set_input_files(str(fixture))
            for _ in range(2):
                broken.locator('#player').evaluate('el => {el.play().catch(()=>{});}')
                expect(broken.locator('#state')).to_contain_text('Audio analysis unavailable')
                assert broken.locator('#player').evaluate('el => el.paused')
            broken.locator('#export').click()
            expect(broken.locator('#state')).to_contain_text('No captured controls')
            browser.close()
        print('PASS: native audio analysis, per-packet settings, pause/resume and failed graph')
    finally:
        try: os.killpg(server.pid,signal.SIGTERM)
        except ProcessLookupError: pass
        server.wait(timeout=10)

if __name__ == '__main__': main()
