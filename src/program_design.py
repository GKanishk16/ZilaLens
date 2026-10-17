"""Build M&E design assets with all data-dependent baselines clearly marked pending."""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
ROOT=Path(__file__).resolve().parents[1]

def theory_of_change():
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    fig,ax=plt.subplots(figsize=(12,4)); ax.set_xlim(0,12); ax.set_ylim(0,4); ax.axis('off')
    blocks=[(0.3,'Access','Suitable accounts, reachable agents, reliable connectivity'),(3.25,'Use','Women control and use accounts and digital services'),(6.2,'Livelihoods','Savings, transfers, payments and credit support choices'),(9.15,'Resilience','Greater capacity to manage shocks and plan')]
    for x,h,b in blocks:
        patch=FancyBboxPatch((x,.95),2.45,2,boxstyle='round,pad=0.12',facecolor='#EAF2F8',edgecolor='#1F4E79',linewidth=1.5); ax.add_patch(patch)
        ax.text(x+1.225,2.35,h,ha='center',va='center',fontsize=13,weight='bold',color='#17365D')
        ax.text(x+1.225,1.65,b,ha='center',va='center',fontsize=9,wrap=True)
    for x in [2.8,5.75,8.7]: ax.add_patch(FancyArrowPatch((x,1.95),(x+.4,1.95),arrowstyle='-|>',mutation_scale=16,color='#C47F17',linewidth=1.6))
    ax.text(6,3.55,'ZilaLens programme logic | Assumptions: access is safe, affordable, reliable; women retain agency; services respond to needs.',ha='center',fontsize=10,color='#444')
    p=ROOT/'outputs'/'charts'/'theory_of_change.png'; fig.savefig(p,dpi=200,bbox_inches='tight'); plt.close(fig)

def logframe():
    rows=[
    ['Goal','Women’s economic resilience supported through inclusive financial services','Women reporting ability to meet an unexpected expense / manage a shock','Baseline survey; set after district selection','Target set after baseline','Endline survey','Economic conditions and service availability remain adequate'],
    ['Outcome 1','Women gain access to suitable financial services','Women who have an account that they themselves use','NFHS-4 district baseline available after district selection and crosswalk','Set after validation','NFHS factsheets; field survey','Accounts remain accessible and functional'],
    ['Outcome 2','Women exercise control over account use and transactions','Share of account holders who can transact independently','Field baseline pending','Set after baseline','Household survey; transaction recall','Respondents can answer privately and safely'],
    ['Outcome 3','Digital access and confidence improve','Women who themselves use a mobile phone; digital task competency','NFHS baseline pending common indicator confirmation','Set after baseline','NFHS factsheets; skills assessment','Network, devices and accessible support are available'],
    ['Output 1','Local agent and bank support improves','Functional service points and resolution rate','Baseline mapping pending','Set after mapping','Service point audit; grievance log','Banks and BC networks cooperate'],
    ['Output 2','Women receive practical financial capability support','Participants completing modules; knowledge change','Programme baseline pending','Set after baseline','Attendance and pre/post assessment','Content is accessible and locally relevant'],
    ['Output 3','Peer and referral mechanisms are active','Active groups and completed referrals','Baseline pending','Set after district selection','Group records and referral tracking','Community partners are trusted'],
    ['Activities','Map service availability; co-design training; provide assisted practice; establish referral/grievance pathways; monitor safe use','Delivery completion and quality checks','Not applicable','Quarterly milestones after inception','Activity records; supervision checklists','Staffing and procurement occur on time'],
    ]
    headers=['Level','Result statement','Indicator','Baseline','Target','Means of Verification','Assumptions']
    wb=Workbook(); ws=wb.active; ws.title='Logframe'; ws.append(headers)
    for row in rows: ws.append(row)
    ws.freeze_panes='A2'; ws.auto_filter.ref=ws.dimensions
    widths=[16,44,48,42,28,35,42]
    for i,w in enumerate(widths,1): ws.column_dimensions[chr(64+i)].width=w
    for c in ws[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='17365D'); c.alignment=Alignment(wrap_text=True,vertical='center')
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment=Alignment(wrap_text=True,vertical='top')
    for n in range(2,ws.max_row+1): ws.row_dimensions[n].height=70
    p=ROOT/'outputs'/'tables'/'ZilaLens_Logframe.xlsx'; wb.save(p)

def xlsform():
    questions=[
    ('select_one yesno','consent','Do you agree to take part?','क्या आप भाग लेने के लिए सहमत हैं?','yes',''),
    ('select_one gender','respondent_gender','How do you describe your gender?','आप अपने लिंग का वर्णन कैसे करती/करते हैं?','yes',"${consent}='yes'"),
    ('integer','age','What is your age in completed years?','आपकी आयु पूरी हुई वर्षों में कितनी है?','yes',"${consent}='yes'"),
    ('select_one yesno','account_any','Do you currently have a bank or savings account?','क्या आपके पास अभी बैंक या बचत खाता है?','yes',"${consent}='yes'"),
    ('select_one yesno','account_self_use','Do you personally use this account?','क्या आप स्वयं इस खाते का उपयोग करती/करते हैं?','yes',"${account_any}='yes'"),
    ('select_multiple use_modes','use_mode','How do you use the account? Select all that apply.','आप खाते का उपयोग कैसे करती/करते हैं? सभी लागू विकल्प चुनें।','no',"${account_self_use}='yes'"),
    ('select_one frequency','use_frequency','How often have you used it in the last three months?','पिछले तीन महीनों में आपने इसका कितनी बार उपयोग किया?','yes',"${account_self_use}='yes'"),
    ('select_one yesno','card_access','Do you have access to the debit card or passbook?','क्या आपके पास डेबिट कार्ड या पासबुक तक पहुंच है?','yes',"${account_any}='yes'"),
    ('select_one yesno','pin_private','Can you use your PIN without another person entering it?','क्या आप किसी अन्य व्यक्ति से दर्ज कराए बिना अपना पिन उपयोग कर सकती/सकते हैं?','yes',"${account_any}='yes'"),
    ('select_one yesno','control_decision','Can you decide how money in the account is used?','क्या आप खाते के पैसे के उपयोग का निर्णय स्वयं कर सकती/सकते हैं?','yes',"${account_any}='yes'"),
    ('select_one reasons','nonuse_reason','What is the main reason you do not use the account?','खाते का उपयोग न करने का मुख्य कारण क्या है?','yes',"${account_any}='yes' and ${account_self_use}='no'"),
    ('select_multiple barriers','account_barriers','What makes account use difficult? Select all that apply.','खाते का उपयोग कठिन क्यों है? सभी लागू विकल्प चुनें।','no',"${consent}='yes'"),
    ('select_one yesno','phone_own','Do you have a mobile phone that you personally use?','क्या आपके पास ऐसा मोबाइल फोन है जिसे आप स्वयं उपयोग करती/करते हैं?','yes',"${consent}='yes'"),
    ('select_one yesno','phone_private','Can you use the phone when you need it?','क्या जरूरत पड़ने पर आप फोन का उपयोग कर सकती/सकते हैं?','yes',"${phone_own}='yes'"),
    ('select_one yesno','internet_use','Have you used the internet in the past 30 days?','क्या आपने पिछले 30 दिनों में इंटरनेट का उपयोग किया है?','yes',"${phone_own}='yes'"),
    ('select_multiple digital_tasks','digital_tasks','Which phone or digital tasks can you do yourself?','आप कौन से फोन या डिजिटल काम स्वयं कर सकती/सकते हैं?','no',"${phone_own}='yes'"),
    ('select_one yesno','digital_safety','Do you feel able to recognize a suspicious financial message or call?','क्या आप संदिग्ध वित्तीय संदेश या कॉल पहचान सकती/सकते हैं?','yes',"${consent}='yes'"),
    ('select_multiple barriers','digital_barriers','What makes digital financial services difficult?','डिजिटल वित्तीय सेवाएं कठिन क्यों हैं?','no',"${consent}='yes'"),
    ('select_one yesno','bank_distance','Is a bank branch or service point reachable within one hour?','क्या बैंक शाखा या सेवा केंद्र एक घंटे में पहुंचा जा सकता है?','yes',"${consent}='yes'"),
    ('select_one frequency','agent_visit','How often is a banking agent available in your village or locality?','आपके गांव या क्षेत्र में बैंकिंग एजेंट कितनी बार उपलब्ध रहता है?','yes',"${consent}='yes'"),
    ('select_one yesno','fees_issue','Have fees or travel costs stopped you from using the account?','क्या शुल्क या यात्रा खर्च ने आपको खाते के उपयोग से रोका है?','yes',"${account_any}='yes'"),
    ('select_one yesno','service_issue','Have you faced a failed transaction in the past three months?','क्या पिछले तीन महीनों में आपका लेनदेन विफल हुआ है?','yes',"${account_any}='yes'"),
    ('select_one yesno','resolved','Was the most recent problem resolved?','क्या हाल की समस्या का समाधान हुआ?','yes',"${service_issue}='yes'"),
    ('select_one yesno','help_person','Do you need another person’s help to use financial services?','क्या वित्तीय सेवाओं के उपयोग के लिए आपको किसी अन्य व्यक्ति की मदद चाहिए?','yes',"${consent}='yes'"),
    ('select_multiple helper_roles','helper_role','Who usually helps you?','आमतौर पर आपकी मदद कौन करता है?','no',"${help_person}='yes'"),
    ('select_one yesno','norm_permission','Do household expectations affect when or where you can use services?','क्या घर की अपेक्षाएं सेवाओं के उपयोग के समय या स्थान को प्रभावित करती हैं?','yes',"${consent}='yes'"),
    ('select_one yesno','training_interest','Would you like practical support to use accounts or digital services?','क्या आप खाते या डिजिटल सेवाओं के उपयोग में व्यावहारिक सहायता चाहेंगी/चाहेंगे?','yes',"${consent}='yes'"),
    ('select_multiple support_topics','support_topic','Which support would be most useful?','कौन सी सहायता सबसे उपयोगी होगी?','no',"${training_interest}='yes'"),
    ('text','open_barrier','What is one change that would make account use easier for you?','कौन सा एक बदलाव खाते का उपयोग आपके लिए आसान करेगा?','no',"${consent}='yes'"),
    ('note','thanks','Thank you. Your responses will be kept confidential.','धन्यवाद। आपके उत्तर गोपनीय रखे जाएंगे।','no',"${consent}='yes'"),
    ('note','declined','Thank you. The interview ends because you did not consent.','धन्यवाद। आपकी सहमति न होने के कारण साक्षात्कार यहीं समाप्त होता है।','no',"${consent}='no'"),
    ]
    choices={
    'yesno':[('yes','Yes','हाँ'),('no','No','नहीं')],
    'gender':[('woman','Woman','महिला'),('man','Man','पुरुष'),('another','Another identity','अन्य पहचान'),('prefer_not','Prefer not to say','बताना नहीं चाहते')],
    'frequency':[('weekly','Weekly or more','साप्ताहिक या अधिक'),('monthly','Monthly','मासिक'),('less','Less often','कम बार'),('never','Never','कभी नहीं')],
    'reasons':[('no_need','No need or no money to transact','जरूरत नहीं या लेनदेन के लिए पैसा नहीं'),('no_access','No card, PIN or access','कार्ड, पिन या पहुंच नहीं'),('distance','Distance or travel cost','दूरी या यात्रा खर्च'),('agent','Agent unavailable','एजेंट उपलब्ध नहीं'),('trust','Trust or safety concern','विश्वास या सुरक्षा की चिंता'),('other','Other','अन्य')],
    'barriers':[('distance','Distance or travel cost','दूरी या यात्रा खर्च'),('hours','Opening hours','खुलने का समय'),('documents','Documents or authentication','दस्तावेज़ या प्रमाणीकरण'),('network','Network or electricity','नेटवर्क या बिजली'),('fees','Fees or charges','शुल्क'),('safety','Safety or fraud concern','सुरक्षा या धोखाधड़ी की चिंता'),('norms','Household or social expectations','पारिवारिक या सामाजिक अपेक्षाएं'),('language','Language or accessibility','भाषा या सुगम्यता'),('other','Other','अन्य')],
    'use_modes':[('deposit','Deposit','जमा'),('withdraw','Withdraw','निकासी'),('transfer','Transfer','हस्तांतरण'),('benefit','Receive benefits','लाभ प्राप्ति'),('save','Save money','बचत'),('bill','Pay bills','बिल भुगतान')],
    'digital_tasks':[('call','Make a call','कॉल करना'),('message','Send a message','संदेश भेजना'),('payment','Make a digital payment','डिजिटल भुगतान'),('balance','Check account balance','खाता शेष देखना'),('none','None of these','इनमें से कोई नहीं')],
    'helper_roles':[('spouse','Spouse','जीवनसाथी'),('child','Child','बच्चा'),('relative','Other relative','अन्य रिश्तेदार'),('agent','Banking agent','बैंकिंग एजेंट'),('friend','Friend','मित्र'),('other','Other','अन्य')],
    'support_topics':[('account','Account access and documents','खाता पहुंच और दस्तावेज़'),('transactions','Practice transactions','लेनदेन का अभ्यास'),('phone','Phone and digital skills','फोन और डिजिटल कौशल'),('safety','Fraud safety','धोखाधड़ी से सुरक्षा'),('complaint','Complaint and grievance support','शिकायत सहायता')]
    }
    wb=Workbook(); s=wb.active;s.title='survey'; s.append(['type','name','label::English (en)','label::Hindi (hi)','required','relevant'])
    for row in questions:s.append(row)
    c=wb.create_sheet('choices');c.append(['list_name','name','label::English (en)','label::Hindi (hi)'])
    for group,items in choices.items():
        for name,en,hi in items:c.append([group,name,en,hi])
    st=wb.create_sheet('settings');st.append(['form_title','form_id','version','default_language']);st.append(['ZilaLens Financial Inclusion Field Validation','zilalens_financial_inclusion','20261018','English (en)'])
    for sh in wb:
        sh.freeze_panes='A2';sh.auto_filter.ref=sh.dimensions
        for cell in sh[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='17365D')
        for col in sh.columns:
            letter=col[0].column_letter; sh.column_dimensions[letter].width=min(52,max(16,max(len(str(x.value or '')) for x in col)+2))
        for row in sh.iter_rows():
            for cell in row:cell.alignment=Alignment(wrap_text=True,vertical='top')
    p=ROOT/'outputs'/'tables'/'ZilaLens_Field_Validation_XLSForm.xlsx';wb.save(p)
    (ROOT/'docs'/'sampling_plan.md').write_text('''# Field validation sampling plan\n\n## Purpose\nValidate the difference between account ownership and women’s independent, recent use, and identify practical service barriers.\n\n## District selection\nSelect 3–5 Uttar Pradesh districts only after the official NFHS-5 data are available, common indicators and boundary crosswalk are verified, and the lowest-performing districts can be ranked reproducibly. No district is preselected in this draft.\n\n## Proposed design\nWithin each selected district, sample 4 blocks, 2 villages per block, and 15 eligible women per village (target 120 interviews per district; 360–600 total). Stratify villages by rural/urban setting where feasible. Within villages, use a documented household listing and random selection; interview one eligible woman per selected household. These are proposed operational parameters, not a power calculation. Revisit after district population frames and field budget are known.\n\n## Eligibility and safeguards\nWomen aged 18–49 are the proposed participants. Obtain informed consent, conduct interviews privately, allow skipping any question, do not collect names or account numbers, and provide a local referral sheet for complaints and financial fraud concerns. Ensure Hindi and locally understood language support.\n\n## Analysis\nReport weighted and unweighted proportions separately where sampling weights are available. Present ownership, recent use, independent control, transaction frequency, and access barriers as distinct measures. Compare self-reported use with available service mapping; do not infer causality.\n''')

def validate_xlsform():
    import sys
    vendor=ROOT/'work'/'vendor'
    if vendor.exists(): sys.path.insert(0,str(vendor))
    from pyxform.xls2xform import convert
    path=ROOT/'outputs'/'tables'/'ZilaLens_Field_Validation_XLSForm.xlsx'
    result=convert(str(path),validate=False,pretty_print=True)
    (ROOT/'work'/'ZilaLens_Field_Validation_XForm.xml').write_text(result.xform)
    return result.warnings

if __name__=='__main__':
    theory_of_change();logframe();xlsform();print(validate_xlsform())
