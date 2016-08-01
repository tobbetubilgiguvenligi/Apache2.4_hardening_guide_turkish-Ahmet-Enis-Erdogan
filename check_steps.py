import argparse
import os.path

hardening_steps_taken = []
mod_security_enabled = os.path.exists('/etc/apache2/mods-enabled/security2.load')
mod_headers_enabled = os.path.exists('/etc/apache2/mods-enabled/headers.load')
steps = ['server_tokens', 'server_signature_hidden', 'directory_access_disabled', 
  'SSI_disabled', 'protect_system_conf', 'limit_unused_http_methods', 'disable_trace_method'
  'change_timeout', 'mod_security_enabled', 'http_only_cookie', 'clickjacking_measure'
  'xss_protection']
def check(path):
  with open(path) as f:
    # apache bilgilerinin gizlenmesi
    for line in f:
      if 'ServerTokens Prod' in line:
        hardening_steps_taken.append('server_tokens')
      if 'ServerSignatures Off' in line:
        hardening_steps_taken.append('server_signature_hidden')
      if 'Options' in line:
        if '-Indexes' in line:
          hardening_steps_taken.append('directory_access_disabled')
        if '-Includes' in line:
          hardening_steps_taken.append('SSI_disabled')
      if 'AllowOverride None' in line:
        hardening_steps_taken.append('protect_system_conf')
      if '<LimitExcept' in line:
        hardening_steps_taken.append('limit_unused_http_methods')
      if 'TraceEnable off' in line:
        hardening_steps_taken.append('disable_trace_method')
      if 'Timeout' in line:
        hardening_steps_taken.append('change_timeout')
      if mod_security_enabled:
        hardening_steps_taken.append('mod_security_enabled')
      if mod_headers_enabled:
        if 'Header edit Set-Cookie ^(.*)$ $1;HttpOnly;Secure' in line:
          hardening_steps_taken.append('http_only_cookie')
        if 'Header always append X-Frame-Options SAMEORIGIN' in line:
          hardening_steps_taken.append('clickjacking_measure')
        if 'Header X-XSS-Protection "1; mode=block"' in line:
          hardening_steps_taken.append('xss_protection')



if __name__ == "__main__": 
  parser = argparse.ArgumentParser()
  
  parser.add_argument("-m","--main_conf",
                  help="path to the main conf file")
  parser.add_argument("-s", "--secondary_conf",
                  help="secondary conf file i.e. file for virtualhost" + 
                  " '/etc/apache2/sites-enabled/000-default.conf'")
  
  args = parser.parse_args()
  main_conf_path = '/etc/apache2/apache2.conf'

  if args.main_conf:
    main_conf_path = args.main_conf

  check(main_conf_path)

  if args.secondary_conf:
    check(args.secondary_conf)

  unimplemented_steps = set(steps).difference(set(hardening_steps_taken))
  score = len(set(hardening_steps_taken)) / float(len(steps))
  print 'hardening steps taken', set(hardening_steps_taken)
  print 'unimplemented steps', unimplemented_steps
  print 'overall score %d/100' % (100*(score))

