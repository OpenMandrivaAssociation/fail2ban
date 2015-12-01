Summary:	Ban IPs that make too many password failures

Name:		fail2ban
Version:	0.9.3
Release:	3
License:	GPLv2+
Group:		System/Configuration/Networking
URL:		http://fail2ban.sourceforge.net/
Source0:	https://github.com/downloads/fail2ban/fail2ban/%{name}-%{version}.tar.gz
Patch0:		%{name}-0.9.3-jail-conf.patch
Patch1:		fail2ban_0.9.3-log-actions-to-SYSLOG.patch
BuildRequires:	pkgconfig(python2)
BuildRequires:	systemd
BuildRequires:	help2man
Requires:	python >= 2.5
Requires:	tcp_wrappers >= 7.6-29
Requires:	iptables >= 1.3.5-3
Suggests:	python-gamin
Suggests:	python-dnspython
BuildArch:	noarch
Requires(pre):	rpm-helper

%description
Fail2Ban scans log files like /var/log/secure and bans IP that makes
too many password failures. It updates firewall rules to reject the IP
address. These rules can be defined by the user. Fail2Ban can read
multiple log files including sshd or Apache web server logs.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%serverbuild_hardened
env CFLAGS="%{optflags}" %{__python} setup.py build

pushd man
sh generate-man
popd

%install
%{__python} setup.py install --root=%{buildroot}

install -d %{buildroot}/%{_mandir}/man1
install man/*.1 %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_unitdir}

install -d %{buildroot}/%{_var}/run/%{name}
install -d %{buildroot}/%{_var}/lib/%{name}

cat > %{buildroot}%{_sysconfdir}/%{name}/jail.d/00-systemd.conf <<EOF
# By defaul use python-systemd backend to access journald
[DEFAULT]
backend=systemd
EOF

# remove non-Linux actions
rm -rf %{buildroot}%{_sysconfdir}/%{name}/action.d/*ipfw.conf
rm -rf %{buildroot}%{_sysconfdir}/%{name}/action.d/{ipfilter,pf,ufw}.conf
rm -rf %{buildroot}%{_sysconfdir}/%{name}/action.d/osx-*.conf

# remove docs
rm -r %{buildroot}%{_docdir}/%{name}

%files
%doc ChangeLog README TODO
%{_unitdir}/%{name}.service
%{_bindir}/%{name}-*
%config(noreplace) %{_sysconfdir}/%{name}/jail.d/00-systemd.conf
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
%dir %{_var}/lib/%{name}
%ghost %dir %{_var}/run/%{name}
%{_datadir}/%{name}/client/*.py*
%{_datadir}/%{name}/server/*.py*
%{_datadir}/%{name}/common/*.py*
%{_datadir}/%{name}/*-info
%{_mandir}/man1/*

