from pathlib import Path
import json,re,io
import pymupdf as fitz
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
original=fitz.open(ROOT.parent/'sample_report.pdf')
report=fitz.open(ROOT/'reports/InterviewRecall_Project_Report.pdf')
assert len(original)==len(report)==45
checks=json.loads((ROOT/'reports/source/layout-checks.json').read_text())
assert not checks['fit_issues'],checks['fit_issues']
alltext='\n'.join(p.get_text() for p in report)
ids=set(re.findall(r'RA\d{13}',alltext))
assert ids=={'RA2311003011898','RA2311003011910','RA2311003011900'},ids
for page in [0,1,2,40]:
 assert ids <= set(re.findall(r'RA\d{13}', report[page].get_text())),page+1
assert 'Pranav' in report[12].get_text()
for old in ['Anahita','Iraa','preplate_db','47 tests','56.5 percent','42.9 percent','RA2311003011794','RA2311003010374']:
 assert old.lower() not in alltext.lower(),old
footers=[];wide=[]
for i,(ref,p) in enumerate(zip(original,report)):
 assert ref.rect==p.rect
 spans=[s for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans'] if s['text'].strip()]
 for s in spans:
  if s['bbox'][0]<65 or s['bbox'][2]>555:wide.append((i+1,s['text']))
 if i:
  label=['i','ii','iii','iv','v','vi','vii'][i-1] if i<8 else str(i-7)
  nums=[s for s in spans if s['text'].strip()==label and s['bbox'][1]>790]
  assert len(nums)==1,(i+1,label,nums)
  center=(nums[0]['bbox'][0]+nums[0]['bbox'][2])/2
  assert abs(center-p.rect.width/2)<1,(i+1,center)
  # The source's bottom-center numbering is retained, including font and exact baseline.
  a=Image.open(io.BytesIO(ref.get_pixmap(clip=fitz.Rect(0,790,p.rect.width,p.rect.height)).tobytes('png')))
  b=Image.open(io.BytesIO(p.get_pixmap(clip=fitz.Rect(0,790,p.rect.width,p.rect.height)).tobytes('png')))
  assert ImageChops.difference(a,b).getbbox() is None,('footer changed',i+1)
  footers.append({'page':i+1,'label':label,'baseline':nums[0]['origin'][1]})
assert not wide,wide
# Institutional cover content, degree, logo, and department are unchanged below the team block.
a=Image.open(io.BytesIO(original[0].get_pixmap(clip=fitz.Rect(0,285,595.2,790)).tobytes('png')))
b=Image.open(io.BytesIO(report[0].get_pixmap(clip=fitz.Rect(0,285,595.2,790)).tobytes('png')))
assert ImageChops.difference(a,b).getbbox() is None
result={'template':'Corrected original PrePlate sample_report.pdf','pages':45,'page_sizes_match':True,'original_cover_institutional_region_pixel_identical':True,'original_44_bottom_center_footers_pixel_identical':True,'team_registration_numbers':sorted(ids),'fixed_frame_fit_issues':0,'wide_text_spans':wide,'footers':footers}
(ROOT/'reports/source/verification.json').write_text(json.dumps(result,indent=2))
print('Verified: 45 pages; original page dimensions, cover institutional content and 44 bottom-center footers preserved; all three correct team IDs; no text-frame overflow.')
