Summary:	Ban IPs that make too many password failures
Name:		fail2ban
Version:	0.9.3
Release:	%mkrel .1
License:	GPLv2+
Group:		System/Configuration/Networking
URL:		http://fail2ban.sourceforge.net/
Source0:	https://github.com/downloads/fail2ban/fail2ban/%{name}_%{version}.tar.gz
Source1:	%{name}.service
Patch0:		%{name}-0.9.3-jail-conf.patch
Patch1:		fail2ban_0.9.3-log-actions-to-SYSLOG.patch
Requires(pre):	rpm-helper
BuildRequires:	python-devel
Requires:	python		>= 2.5
Requires:	tcp_wrappers	>= 7.6-29
Requires:	iptables	>= 1.3.5-3
Suggests:	python-gamin
%py_requires -d
BuildArch:	noarch
%if %mdkver >= 201100
BuildRequires:	systemd-units
Requires(post,preun): systemd-units
%endif

BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
Fail2Ban scans log files like /var/log/secure and bans IP that makes
too many password failures. It updates firewall rules to reject the IP
address. These rules can be defined by the user. Fail2Ban can read
multiple log files including sshd or Apache web server logs.

%prep
%setup -qn fail2ban-%{version}
%patch0 -p1
%patch1 -p1

%build
%serverbuild_hardened
env CFLAGS="%{optflags}" python setup.py build

pushd man
sh generate-man
popd

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

python setup.py install --root=%{buildroot}

install -d %{buildroot}/%{_mandir}/man1
install man/*.1 %{buildroot}%{_mandir}/man1/
%if %mdkver >= 201100
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
%else
install -D files/redhat-initd  %{buildroot}/%{_initrddir}/%{name}
%endif

install -d %{buildroot}/%{_var}/run/%{name}

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%post
%_post_service fail2ban

%preun
%_preun_service fail2ban

%files
%defattr(-,root,root)
%doc ChangeLog README TODO

%if %mdkver >= 201100
%{_unitdir}/%{name}.service
%else
%attr(744,root,root) %{_initrddir}/%{name}
%endif

%{_bindir}/%{name}-*
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/action.d/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/filter.d/*.conf
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/action.d
%dir %{_sysconfdir}/%{name}/filter.d
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/client
%dir %{_datadir}/%{name}/server
%dir %{_datadir}/%{name}/common
%ghost %dir %{_var}/run/%{name}
%{_datadir}/%{name}/client/*.py*
%{_datadir}/%{name}/server/*.py*
%{_datadir}/%{name}/common/*.py*
%{_datadir}/%{name}/*-info
%{_mandir}/man1/*


%changelog
* Sun Feb 19 2012 Tomasz Pawel Gajc <tpg@mandriva.org> 0.8.6-2mdv2012.0
+ Revision: 777475
- Patch 4: fix dictionary table (from <wojo@narzedziowka.com> )
- set type to forking for service

* Sun Jan 15 2012 Tomasz Pawel Gajc <tpg@mandriva.org> 0.8.6-1
+ Revision: 761456
- update to new version 0.8.6
- provide systemd unit service
- drop patch 1
- Patch2: fix init script
- Patch3: log output to SYSLOG

* Sun Oct 31 2010 Funda Wang <fwang@mandriva.org> 0.8.4-3mdv2011.0
+ Revision: 590802
- rebuild for py2.7

* Thu Sep 24 2009 Frederik Himpe <fhimpe@mandriva.org> 0.8.4-2mdv2010.0
+ Revision: 448503
- Suggests python-gamin so that faster gamin back-end instead of polling
  is used

* Wed Sep 09 2009 Frederik Himpe <fhimpe@mandriva.org> 0.8.4-1mdv2010.0
+ Revision: 435890
- Update to new version 0.8.4

* Sun Jul 26 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 0.8.3-3mdv2010.0
+ Revision: 400456
- Patch1: Set the file descriptor to be FD_CLOEXEC
- remove sock in case of unclean shutdown in initscript

* Sun Dec 28 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 0.8.3-2mdv2009.1
+ Revision: 320115
- rebuild for python-2.6

* Sat Jul 19 2008 Emmanuel Andry <eandry@mandriva.org> 0.8.3-1mdv2009.0
+ Revision: 238790
- New version

* Fri May 30 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 0.8.2-2mdv2009.0
+ Revision: 213376
- Patch0: fix ssh log path (#40792), and enable by default ssh-iptables
- create missing directory (#40793)

* Sat Mar 08 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 0.8.2-1mdv2008.1
+ Revision: 182153
- fix docs
- update init script
- new version

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sat Nov 17 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.8.1-1mdv2008.1
+ Revision: 109496
- new version
- new license policy
- drop patch 0, fixed upstream
- add patch 0 (ssh)

* Mon May 07 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.8.0-1mdv2008.0
+ Revision: 24052
- new version


* Tue Feb 13 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.7.7-1mdv2007.0
+ Revision: 120339
- new version
- provide better initscript
- drop patches
- spec file clean

* Sat Jan 06 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.7.6-1mdv2007.1
+ Revision: 104919
- forgot to add patch 0 into svn :(
- update to the latest version
- regenerate patches 0,1,2,3
- add patch 4
- add %%postun

* Sat Dec 30 2006 Tomasz Pawel Gajc <tpg@mandriva.org> 0.7.5-4mdv2007.1
+ Revision: 102842
- regenerate fail2ban-server patch

* Sat Dec 30 2006 Tomasz Pawel Gajc <tpg@mandriva.org> 0.7.5-3mdv2007.1
+ Revision: 102829
- fix module path

* Sat Dec 30 2006 Tomasz Pawel Gajc <tpg@mandriva.org> 0.7.5-2mdv2007.1
+ Revision: 102765
- changed %%py_platsitedir to %%py_puresitedir
- Import fail2ban

