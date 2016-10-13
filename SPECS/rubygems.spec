%define _buildid .12

# Upstream git:
# https://github.com/rubygems/rubygems.git
#
%global rubygems_dir %(ruby1.8 -rrbconfig -e 'puts Config::CONFIG["sitelibdir"]')
%global ruby_ver     %(ruby1.8 -rrbconfig -e 'puts RbConfig::CONFIG["ruby_version"][0..2]')

# Specify custom RubyGems root and other related macros.
%global gem_dir      %(ruby1.8 -rrbconfig -e 'puts File::expand_path(File::join(Config::CONFIG["sitedir"],"..","gems"))')/%ruby_ver

# TODO: These folders should go into rubygem-filesystem but how to achieve it,
# since noarch package cannot provide arch dependent subpackages?
# http://rpm.org/ticket/78
%global gem_extdir   %{_exec_prefix}/lib{,64}/gems/%ruby_ver

# Executing testsuite (enabling %%check section) will cause dependency loop.
# To avoid dependency loop when necessary, please set the following value to 0
%global	enable_check 1

# It cannot be relied on %%{_libdir} for noarch packages. Query Ruby for
# the right value.
# https://fedorahosted.org/rel-eng/ticket/5257
%{!?buildtime_libdir:%global buildtime_libdir $(ruby1.8 -rrbconfig -e 'puts RbConfig::CONFIG["libdir"]')}

%global obsolete_ver 1.8.25

Summary:	The Ruby standard for packaging ruby libraries
Name:		rubygems18
Version:	1.8.25
Release: 9%{?_buildid}%{?dist}
Group:		Development/Libraries
License:	Ruby or MIT

URL:		https://rubygems.org/
Source0:	http://production.cf.rubygems.org/rubygems/rubygems-%{version}.tgz
# http://seclists.org/oss-sec/2013/q3/att-576/check_CVE-2013-4287_rb.bin
# Slightly modified for exit status
Source10:	check_CVE-2013-4287.rb
# http://seclists.org/oss-sec/2013/q3/att-621/check_CVE-2013-XXXX_rb.bin
# Slightly modified for exit status,
# Also modified to match:
# http://seclists.org/oss-sec/2013/q3/605
Source11:	check_CVE-2013-4363.rb

# Sources from the works by Vít Ondruch <vondruch@redhat.com>
# Please keep Source100 and Patch{105,109} in sync with ruby.spec

Source100:	operating_system.rb

# Kill patch0 for ruby 1.9.x
Patch0:		rubygems-1.8.5-noarch-gemdir.patch
# Will discuss upstream
# https://github.com/rubygems/rubygems/issues/120
# rubygems-Patches-28631
Patch1:		rubygems-1.8.6-show-extension-build-process-in-sync.patch
# rubygems-Patches-29049
# https://github.com/rubygems/rubygems/issues/118
Patch3:		rubygems-1.8.5-show-rdoc-process-verbosely.patch
# Fix Gem.all_load_paths (although it is deprecated and will be removed
# on 2011-10-01)
# Fixed in 1.8.22
#Patch6:		rubygems-1.8.5-all-load-paths.patch
# Backport from 1.8.26 to fix CVE-2013-4287
# Note that 1.8.26 uses minitest ~> 4.0 for test suite, which is
# not available on F-18, so we cannot easily update to 1.8.26
Patch4:		rubygems-1.8.25-CVE-2013-4287.patch
# http://seclists.org/oss-sec/2013/q3/att-634/CVE-2013-XXXX_1_8.patch
# Kill for broken test part
Patch5:		rubygems-1.8.26-CVE-2013-4363.patch

# Patches from the works by Vít Ondruch <vondruch@redhat.com>
# Fix the uninstaller, so that it doesn't say that gem doesn't exist
# when it exists outside of the GEM_HOME (already fixed in the upstream)
Patch105:	ruby-1.9.3-rubygems-1.8.11-uninstaller.patch
# Add support for installing binary extensions according to FHS.
# https://github.com/rubygems/rubygems/issues/210
Patch109:	rubygems-1.8.11-binary-extensions.patch
BuildArch:	noarch

BuildRequires:  ruby18
BuildRequires:	ruby18-devel
%if %{enable_check}
BuildRequires:	rubygem18(minitest)
BuildRequires:	rubygem18(rake)
# rdoc became a gem
BuildRequires:	rubygem18(rdoc)       >= 3.9.4
# BuildRequires:  ruby18-rdoc
# Only required if Ruby >= 1.9.2
# BuildRequires:	rubygem%{ruby_ver}(io-console) >= 0.3
%endif
%if 0%{?rhel} < 6
BuildRequires:  openssl
%else
BuildRequires:  ca-certificates
%endif

Requires:       ruby18
# rdoc became a gem
Requires:	rubygem18(rdoc)       >= 3.9.4
#Requires:       ruby18-rdoc
# Only required if Ruby >= 1.9.2
# Requires:	rubygem18(io-console) >= 0.3
%if 0%{?rhel} < 6
Requires:       openssl
%else
Requires:	ca-certificates
%endif

Provides:       rubygems18                = %{version}-%{release}
Provides:	ruby(rubygems)            = %{version}-%{release}
Provides:       ruby18(rubygems)          = %{version}-%{release}
Provides:       gem                       = %{version}-%{release}
Provides:       gem18                     = %{version}-%{release}
Obsoletes:      rubygems                 <= %{obsolete_ver}

%description
RubyGems is the Ruby standard for publishing and managing third party
libraries.

%package 	devel
Summary:	Macros and development tools for packagin RubyGems
Group:		Development/Libraries
License:	Ruby or MIT
Requires:	%{name} = %{version}-%{release}
Provides:       rubygems18-devel
Obsoletes:      rubygems-devel <= %{obsolete_ver}
BuildArch:	noarch

%description	devel
Macros and development tools for packagin RubyGems.

%prep
%setup -q -n rubygems-%{version}
%patch0 -p1 -b .noarch
%if 1
%patch1 -p1 -b .insync
%patch3 -p1 -b .rdoc_v
%patch4 -p1 -b .cve-2013-4287
%patch5 -p1 -b .cve-2013-4363
#%%patch6 -p1 -b .load_path
%endif
%patch105 -p1 -b .uninst
%patch109 -p1 -b .bindir

# Some of the library files start with #! which rpmlint doesn't like
# and doesn't make much sense
for f in `find lib -name \*.rb` ; do
  head -1 $f | grep -q '^#!/usr/bin/env ruby' && sed -i -e '1d' $f
done

%build
# Nothing

%install
GEM_HOME=%{buildroot}/%{gem_dir} \
    ruby1.8 setup.rb --rdoc --prefix=/ \
        --destdir=%{buildroot}/%{rubygems_dir}/

mkdir -p %{buildroot}/%{_bindir}
mv %{buildroot}/%{rubygems_dir}/bin/gem1.8 %{buildroot}/%{_bindir}/gem1.8
rm -rf %{buildroot}/%{rubygems_dir}/bin
mv %{buildroot}/%{rubygems_dir}/lib/* %{buildroot}/%{rubygems_dir}/.

# Install custom operating_system.rb.
# Currently breaks Ruby 1.8
# mkdir -p %{buildroot}%{rubygems_dir}/rubygems/defaults
# install -cpm 0644 %{SOURCE100} %{buildroot}%{rubygems_dir}/rubygems/defaults/

# Create empty file we own but have alternatives manage the content
touch %{buildroot}%{_bindir}/gem

# Kill bundled cert.pem
mkdir -p %{buildroot}%{rubygems_dir}/rubygems/ssl_certs/
ln -sf %{_sysconfdir}/pki/tls/cert.pem \
        %{buildroot}%{rubygems_dir}/rubygems/ssl_certs/ca-bundle.pem

# Make sure Ruby 1.8 is always used, even if alternatives points elsewhere
for i in $(find %{buildroot} -type f); do
    sed -i -re '1s|^#!/usr/bin/(env )?ruby.*|#!/usr/bin/env ruby1.8|' $i
done

sed -i -re 's|shebang = "#!/usr/bin/ruby"|shebang = "#!/usr/bin/env ruby%{ruby_ver}"|' \
    %{buildroot}%{rubygems_dir}/rubygems/installer_test_case.rb

# Create gem folders.
mkdir -p %{buildroot}%{gem_dir}/{cache,gems,specifications,doc}
mkdir -p %{buildroot}%{gem_extdir}/exts

# Create macros.rubygems file for rubygems-devel
mkdir -p %{buildroot}%{_sysconfdir}/rpm

cat >> %{buildroot}%{_sysconfdir}/rpm/macros.%{name} << \EOF
# Taken from ruby18 spec file
%%_normalized_cpu %%(echo %%{_target_cpu} | sed 's/^ppc/powerpc/;s/i.86/i386/;s/sparcv./sparc/')
# The RubyGems root folder.
%%gem18_dir %{gem_dir}

# Common gem locations and files.
%%gem18_instdir    %%{gem18_dir}/gems/%%{gem_name}-%%{version}/
%%gem18_extdir     %%{_libdir}/ruby/site_ruby/1.8/%%{_normalized_cpu}-%%{_target_os}/%%{gem_name}
%%gem18_libdir     %%{gem18_instdir}/lib/
%%gem18_cache      %%{gem18_dir}/cache/%%{gem_name}-%%{version}.gem
%%gem18_spec       %%{gem18_dir}/specifications/%%{gem_name}-%%{version}.gemspec
%%gem18_docdir     %%{gem18_dir}/doc/%%{gem_name}-%%{version}/

# Install gem into appropriate directory.
# -n<gem_file>      Overrides gem file name for installation.
# -d<install_dir>   Set installation directory.
%%gem18_install(d:n:) \
mkdir -p %%{-d*}%%{!?-d:.%%{gem18_dir}} \
\
CONFIGURE_ARGS="--with-cflags='%%{optflags}' $CONFIGURE_ARGS" \\\
gem%{ruby_ver} install \\\
        -V \\\
        --local \\\
        --install-dir %%{-d*}%%{!?-d:.%%{gem18_dir}} \\\
        --bindir .%%{_bindir} \\\
        --force \\\
        --rdoc \\\
        %%{-n*}%%{!?-n:%%{gem_name}-%%{version}.gem} \
%%{nil}
EOF

%if %{enable_check}
%check
# Create an empty operating_system.rb, so that the system's one doesn't get used,
# otherwise the test suite fails.
mkdir -p lib/rubygems/defaults
touch lib/rubygems/defaults/operating_system.rb

# It is necessary to specify the paths using RUBYOPT to let the test suite pass."
export GEM_PATH=%{gem_dir}
RUBYOPT="-Itest -Ilib" 
for dir in \
	%{buildtime_libdir}/gems/exts/io-console-*/lib/ \
	%{gem_dir}/gems/json-*/lib \
%if 0%{?fedora} < 19
	%{buildtime_libdir}/gems/exts/json-*/ext/json/ext
%else
	%{buildtime_libdir}/gems/exts/json-*/lib
%endif
do
	RUBYOPT="$RUBYOPT -I$dir"
done
export RUBYOPT

testrb1.8 test

# CVE vulnerability check
ruby1.8 -Ilib %{SOURCE10}
ruby1.8 -Ilib %{SOURCE11}
%endif

%post
# If gem isn't a symlink, we're updating rubygems from a version without alternatives.
# /etc/alternatives/gem must exist because we require a Ruby that sets it up.
if [ ! -L %{_bindir}/gem ]; then
    ln -sf /etc/alternatives/gem %{_bindir}/gem
fi

%files
%doc README* 
%doc History.txt
%doc MIT.txt LICENSE.txt
%dir %{gem_dir}
%dir %{gem_dir}/cache
%dir %{gem_dir}/gems
%dir %{gem_dir}/specifications
%dir %{gem_dir}/doc
%ghost %{_bindir}/gem
%{_bindir}/gem%{ruby_ver}

%dir %{rubygems_dir}/
%{rubygems_dir}/rbconfig/
%{rubygems_dir}/rubygems/
%{rubygems_dir}/rubygems.rb
%{rubygems_dir}/ubygems.rb
%{rubygems_dir}/gauntlet_rubygems.rb

%dir %{_exec_prefix}/lib/gems/%{ruby_ver}
%dir %{_exec_prefix}/lib64/gems/%{ruby_ver}
%dir %{_exec_prefix}/lib/gems/%{ruby_ver}/exts
%dir %{_exec_prefix}/lib64/gems/%{ruby_ver}/exts

%files	devel
%config(noreplace)  %{_sysconfdir}/rpm/macros.%{name}

%changelog
* Fri Nov  6 2015 Alex Yamauchi <alex.yamauchi@hotschedules.com>
- Setting the doc dir to a %dir type in the %files list.

* Fri Mar 14 2014 Lee Trager <ltrager@amazon.com>
- Fix gem18_extdir macro

* Wed Mar 12 2014 Lee Trager <ltrager@amazon.com>
- Use rubygem18-rdoc instead of ruby18-rdoc
- Reenable tests
- Disable tests for boot straping rake
- Remove %global from macros.rubygems18
- Fix extdir macro to conform to Ruby 1.8 standard
- Ensure we're building against Ruby 1.8

* Tue Mar 11 2014 Lee Trager <ltrager@amazon.com>
- Until we have versioned minitest and rake pull in the Ruby 1.8 builds by pkg version
- Add missing '/' to the end of RPM macros
- Obsolete the unversioned rubyems
- Rename to rubygems18

* Tue Oct 15 2013 Lee Trager <ltrager@amazon.com>
- import source package F18/rubygems-1.8.25-8.fc18

* Tue Sep 24 2013 Lee Trager <ltrager@amazon.com>
- Don't use operating_systems.rb with Ruby 1.8
- Reenable tests

* Mon Sep 23 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.8.25-8
- Patch for CVE-2013-4363

* Mon Sep 23 2013 Lee Trager <ltrager@amazon.com>
- Provide versioned devel package
- Teach operating_systems.rb about where we install things in AL
- Use Ruby 1.8 deps

* Thu Sep 19 2013 Lee Trager <ltrager@amazon.com>
- import source package F18/rubygems-1.8.25-7.fc18

* Tue Sep 10 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.8.25-7
- Backport from 1.8.26 to fix CVE-2013-4287

* Fri Sep 6 2013 Tom Kirchner <tjk@amazon.com>
- Fix upgrades to alternatives version of rubygems

* Fri Sep 6 2013 Lee Trager <ltrager@amazon.com>
- Force use with Ruby-1.8

* Tue Mar 26 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.8.25-6
- Fix %%gem_extdir_mri directory on F-18 and below

* Fri Mar  8 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.8.25-5
- Detect json / io-console directory at %%check
- Prevent squash of %%gem_install with following line
  (Vít Ondruch <vondruch@redhat.com>)

* Mon Feb 25 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.8.25-4
- Backport %%gem_extdir_mri also

* Mon Feb 25 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.8.25-3
- And slightly change %%gem_install because rubygems 1.8.25
  does not support --document=ri,rdoc style
  (Vít Ondruch <vondruch@redhat.com>)

* Mon Feb 25 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.8.25-2
- Backport %%gem_install macro

* Tue Feb  5 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.8.25-1
- 1.8.25

* Tue Feb  5 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.8.24-4
- Bump release

* Wed Jan 16 2013 Lee Trager <ltrager@amazon.com>
- On RHEL5 certs are included in the OpenSSL package
- Define build root for RHEL5

* Wed Sep 05 2012 Vít Ondruch <vondruch@redhat.com> - 1.8.24-3
- Fixed Fedora 18 mass rebuild issue.

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.24-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May 2 2012 Lee Trager <ltrager@amazon.com>
- import source package F16/rubygems-1.8.11-3.fc16.1

* Sat Apr 28 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.24-1
- 1.8.24

* Sat Apr 21 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.23-20
- 1.8.23
- Use system-wide cert.pem

* Wed Apr 18 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.22-1
- 1.8.22

* Thu Jan 26 2012 Vít Ondruch <vondruch@redhat.com> - 1.8.15-2
- Make test suite green.

* Thu Jan 26 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.15-1
- 1.8.15

* Thu Jan 26 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.11-10
- Incorpolate works by Vít Ondruch <vondruch@redhat.com>
  made for ruby 1.9.x

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Nov 11 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.11-1
- 1.8.11

* Sun Aug 28 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.10-1
- 1.8.10

* Thu Aug 25 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.9-1
- 1.8.9

* Sun Aug 21 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.8-1
- 1.8.8

* Sat Aug  6 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7-1
- 1.8.7

* Wed Jul 27 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.6-1
- 1.8.6

* Sat Jun 25 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.5-2
- Fix Gem.latest_load_paths (for rubygem-gettext FTBFS)
- Fix Gem.all_load_paths (for rubygem-gettext FTBFS, although it is already
  deprecated from 1.7.0)

* Wed Jun  1 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.5-1
- Try 1.8.5

* Tue May 24 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.7.2-2
- Handle gemspec file with containing "invalid" date format
  generated with psych (ref: bug 706914)

* Sat Apr 30 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.7.2-1
- Update to 1.7.2

* Sat Mar 12 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.6.2-1
- Update to 1.6.2

* Fri Mar  4 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.6.1-1
- Update to 1.6.1
- Patch2, 4 upstreamed

* Thu Mar  3 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.6.0-1
- Update to 1.6.0

* Sun Feb 27 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.5.3-1
- Update to 1.5.3

* Sun Feb 20 2011 Mamoru Tasaka <mtasaka@fedorapeople.org> - 1.5.2-1
- Update to 1.5.2
- Show rdoc process verbosely in verbose mode

* Fri Feb 11 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.5.0-2
- Modify in-sync patch to keep the original behavior (for testsuite)
- Patch to make testsuite succeed, enabling testsuite

* Thu Feb 10 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.5.0-1
- Update to 1.5.0

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 18 2011 Cristian Gafton <gafton@amazon.com>
- update to version 1.3.7

* Thu Dec 2 2010 Cristian Gafton <gafton@amazon.com>
- import source package RHEL6/rubygems-1.3.7-1.el6

* Fri Oct  8 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.3.7-2
- Show build process of extension library in sync

* Fri Jul 9 2010 Cristian Gafton <gafton@amazon.com>
- import source package RHEL6/rubygems-1.3.5-1.el6
- setup complete for package rubygems

* Mon May 17 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.3.7-1
- Update to 1.3.7, dropping upstreamed patch

* Wed Apr 28 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.3.6-1
- Update to 1.3.6
- Show prefix with gem contents by default as shown in --help

* Mon Sep 21 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.3.5-1
- Update to 1.3.5

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Nov 09 2008 Jeroen van Meeuwen <kanarip@kanarip.com> - 1.3.1-1
- New upstream version

* Tue Sep 16 2008 David Lutterkort <dlutter@redhat.com> - 1.2.0-2
- Bump release because I forgot to check in newer patch

* Tue Sep 16 2008 David Lutterkort <dlutter@redhat.com> - 1.2.0-1
- Updated for new setup.rb
- Simplified by removing conditionals that were needed for EL-4;
  there's just no way we can support that with newer rubygems

* Wed Sep  3 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.9.4-2
- fix license tag

* Fri Jul 27 2007 David Lutterkort <dlutter@redhat.com> - 0.9.4-1
- Conditionalize so it builds on RHEL4

* Tue Feb 27 2007 David Lutterkort <dlutter@redhat.com> - 0.9.2-1
- New version
- Add patch0 to fix multilib sensitivity of Gem::dir (bz 227400)

* Thu Jan 18 2007 David Lutterkort <dlutter@redhat.com> - 0.9.1-1
- New version; include LICENSE.txt and GPL.txt
- avoid '..' in gem_dir to work around a bug in gem installer
- add ruby-rdoc to requirements

* Tue Jan  2 2007 David Lutterkort <dlutter@redhat.com> - 0.9.0-2
- Fix gem_dir to be arch independent
- Mention dual licensing in License field

* Fri Dec 22 2006 David Lutterkort <dlutter@redhat.com> - 0.9.0-1
- Updated to 0.9.0
- Changed to agree with Fedora Extras guidelines

* Mon Jan  9 2006 David Lutterkort <dlutter@redhat.com> - 0.8.11-1
- Updated for 0.8.11

* Sun Oct 10 2004 Omar Kilani <omar@tinysofa.org> 0.8.1-1ts
- First version of the package
