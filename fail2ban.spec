Summary:	Ban IPs that make too many password failures
Name:		fail2ban
Version:	0.8.2
Release:	%mkrel 1
License:	GPLv2+
Group:		System/Configuration/Networking
URL:		http://fail2ban.sourceforge.net/
Source0:	http://dl.sourceforge.net/fail2ban/%{name}-%{version}.tar.bz2
Source1:	%{name}-initscript
Requires(pre):	rpm-helper
BuildRequires:	python-devel
Requires:	python		>= 2.5
Requires:	tcp_wrappers	>= 7.6-29
Requires:	iptables	>= 1.3.5-3
%py_requires -d
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
Fail2Ban scans log files like /var/log/secure and bans IP that makes
too many password failures. It updates firewall rules to reject the IP
address. These rules can be defined by the user. Fail2Ban can read
multiple log files including sshd or Apache web server logs.

%prep
%setup -q

%build
env CFLAGS="%{optflags}" python setup.py build 

pushd man
sh generate-man
popd

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

python setup.py install --root=%{buildroot}

install -d %{buildroot}/%{_mandir}/man1
install man/*.1 %{buildroot}%{_mandir}/man1/
install -D %{SOURCE1} %{buildroot}/%{_initrddir}/%{name}

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%post
%_post_service fail2ban

%preun
%_preun_service fail2ban

%files
%defattr(-,root,root)
%doc CHANGELOG README TODO
%attr(744,root,root) %{_initrddir}/%{name}
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
%{_datadir}/%{name}/client/*.py*
%{_datadir}/%{name}/server/*.py*
%{_datadir}/%{name}/common/*.py*
%{_datadir}/%{name}/*-info
%{_mandir}/man1/*
