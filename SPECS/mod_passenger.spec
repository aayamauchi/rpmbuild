%if ! 0%{passenger_major}
%define passenger_major 5
%endif

%if ! 0%{passenger_minor}
%define passenger_minor 0
%endif

%if ! 0%{passenger_release}
%define passenger_minor 26
%endif

%if ! 0%{?apache_major}
%define apache_major 2
%endif

%if ! 0%{?apache_minor}
%define apache_minor 2
%endif

%define apache_version %{apache_major}.%{apache_minor}

%if "%{apache_major}%{apache_minor}" == "22"
%define apache_version_string %{nil}
%else
%define apache_version_string %{apache_major}%{apache_minor}
%endif

%if ! 0%{?ruby_major}
%define ruby_major 1
%endif

%if ! 0%{?ruby_minor}
%define ruby_minor 8
%endif

%define ruby_version %{ruby_major}.%{ruby_minor}

%if "%{ruby_major}%{ruby_minor}" == "18"
%define ruby_version_string %{nil}
%else
%define ruby_version_string %{ruby_major}%{ruby_minor}
%endif

%if ! 0%{?httpd_libdir}
%define httpd_libdir %{_libdir}/httpd/modules
%endif

%if ! 0%{?httpd_configdir}
%define httpd_configdir %{_sysconfdir}/httpd/conf.d
%endif

Name: mod%{apache_version_string}_passenger
Version: %{passenger_major}.%{passenger_minor}.%{passenger_release}
Release: 4%{?dist}
Summary: The Phusion Ruby %{ruby_version} passenger module for Apache %{apache_version}

Group: System Environment/Daemons
License: MIT
URL: https://www.phusionpassenger.com

BuildRequires: rubygem%{ruby_version_string}-passenger
BuildRequires: rubygem%{ruby_version_string}-rack
BuildRequires: gcc-c++
BuildRequires: httpd%{apache_version_string}-devel
BuildRequires: pcre-devel
BuildRequires: libcurl-devel
BuildRequires: zlib-devel
Requires: httpd%{apache_version_string} = %(rpm -q httpd%{apache_version_string}-devel --queryformat '%%{VERSION}-%%{RELEASE}')
Requires: pcre
Requires: rubygem%{ruby_version_string}-passenger = %{version}

%description
The Phusion Ruby %{ruby_version} passenger module for Apache %{apache_version}


%prep
rm -rf passenger-%{version} || :
cp -r /usr/lib/ruby/gems/%{ruby_version}/gems/passenger-%{version} ./
cd passenger-%{version}
#find src -type f -name Makefile \
#    -exec sed -i -e "s@/usr/lib/ruby/gems/1.8/gems@${BUILDROOT}@g" {} \;


%build
export GEM_PATH=%{_builddir}/passenger-%{version}
%if %{passenger_major} > 3
${GEM_PATH}/bin/passenger-install-apache2-module --languages ruby --auto
%else
${GEM_PATH}/bin/passenger-install-apache2-module --auto
%endif


%install
[ -d %{buildroot}%{httpd_libdir} ] \
    || mkdir -p %{buildroot}%{httpd_libdir}
[ -d %{buildroot}%{httpd_configdir} ] \
    || mkdir -p %{buildroot}%{httpd_configdir}

%if %{passenger_major} > 3
install -m 644 %{_builddir}/passenger-%{version}/buildout/apache2/mod_passenger.so \
    %{buildroot}%{httpd_libdir}/mod_passenger.so
%else
install -m 644 %{_builddir}/passenger-%{version}/ext/apache2/mod_passenger.so \
    %{buildroot}%{httpd_libdir}/mod_passenger.so
%endif

unset ${!GEM*}
%if %{passenger_major} > 3
%{_bindir}/passenger-install-apache2-module --snippet \
    | sed -ne '/^<.*>$/,/^<\/.*>$/ {/^<\// s/^/  PassengerEnabled off\n/;p}' \
    > %{buildroot}/%{httpd_configdir}/passenger.conf
%else
LoadModule passenger_module /usr/lib/ruby/gems/1.8/gems/passenger-3.0.21/ext/apache2/mod_passenger.so
PassengerRoot /usr/lib/ruby/gems/1.8/gems/passenger-3.0.21
PassengerRuby /usr/bin/ruby1.8

echo '<IfModule mod_passenger.c>' > %{buildroot}/%{httpd_configdir}/passenger.conf
%{_bindir}/passenger-install-apache2-module --snippet \
    | sed -ne '/LoadModule/ d;s/^/  /' \
    >> %{buildroot}/%{httpd_configdir}/passenger.conf
echo '</IfModule>' >> %{buildroot}/%{httpd_configdir}/passenger.conf
%endif

%clean
rm -rf ${BUILDROOT}/passenger-%{version} || :


%files
%defattr(-,root,root)
%{httpd_libdir}/mod_passenger.so
%config %{httpd_configdir}/passenger.conf


%changelog
* Tue Apr 19 2016 Alex Yamauchi <alex.yamauchi@hotschedules.com>
- Extending to be able to build other versions easily.
- Changing the default Apache version to 2.2.
- Fixing dependencies.

* Thu Apr  7 2016 Alex Yamauchi <alex.yamauchi@hotschedules.com>
- need to pin the specific version-release of httpd as a requirment (release 3).

* Wed Apr  6 2016 Alex Yamauchi <alex.yamauchi@hotschedules.com>
- adding the Apache configuration file, updating to release 2.

* Mon Apr  4 2016 Alex Yamauchi <alex.yamauchi@hotschedules.com>
- initial packaging for Phusion passenger for Apache

