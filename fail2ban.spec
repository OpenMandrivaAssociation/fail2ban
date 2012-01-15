Summary:	Ban IPs that make too many password failures
Name:		fail2ban
Version:	0.8.6
Release:	%mkrel 1
License:	GPLv2+
Group:		System/Configuration/Networking
URL:		http://fail2ban.sourceforge.net/
Source0:	https://github.com/downloads/fail2ban/fail2ban/%{name}_%{version}.orig.tar.gz
Source1:	%{name}.service
Patch0:		%{name}-0.8.2-jail-conf.patch
Patch2:		fail2ban_0.8.6-fix-init-script.patch
Patch3:		fail2ban_0.8.6-log-actions-to-SYSLOG.patch
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
%setup -qn fail2ban-fail2ban-a20d1f8
%patch0 -p1
%patch2 -p1
%patch3 -p1

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
