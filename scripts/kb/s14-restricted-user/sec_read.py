import subprocess,os,time,glob,re,shutil
W='/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work/s14/secread'
shutil.rmtree(W,ignore_errors=True); os.makedirs(W)
open(W+'/package.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><Package xmlns="http://soap.sforce.com/2006/04/metadata"><types><members>Security</members><name>Settings</name></types><version>68.0</version></Package>')
E={**os.environ,'SF_DISABLE_LOG_FILE':'true','SF_SKIP_NEW_VERSION_CHECK':'true'}
p=subprocess.Popen(['sf','project','retrieve','start','--manifest',W+'/package.xml','--target-org','orgfarm-232477b490-dev-ed','--target-metadata-dir',W+'/out','--unzip','--json'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=E,start_new_session=True)
v='READBACK_FAILED'
for i in range(60):
    time.sleep(3); f=glob.glob(W+'/out/**/Security.settings',recursive=True)
    if f:
        time.sleep(1); m=re.search(r'<enableAdminLoginAsAnyUser>(\w+)<',open(f[0]).read()); v=m.group(1) if m else 'NOT_IN_FILE'; break
try: os.killpg(p.pid,9)
except Exception: pass
print('enableAdminLoginAsAnyUser='+v)
