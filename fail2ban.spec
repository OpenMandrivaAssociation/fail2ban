Summary:	Ban IPs that make too many authentication failures
Name:		fail2ban
Version:	0.9.6
Release:	1
License:	GPLv2+
Group:		System/Configuration/Networking
URL:		http://www.fail2ban.org
Source0:	https://github.com/fail2ban/fail2ban/archive/%{version}.tar.gz
Patch0:		%{name}-0.9.4-jail-conf.patch
BuildRequires:	pkgconfig(python3)
BuildRequires:	systemd
BuildRequires:	help2man
Requires:	python >= 2.3
Requires:	tcp_wrappers >= 7.6-29
Suggests:	python-gamin
Suggests:	python-dnspython
Requires(post,preun):   iptables >= 1.3.5-3
Requires(post,preun):   firewalld
Requires:	python-systemd
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

%build
%serverbuild_hardened
env CFLAGS="%{optflags}" %{__python} setup.py build

#pushd man
#sh generate-man
#popd

%install
%{__python} setup.py install --root=%{buildroot}

install -d %{buildroot}/%{_mandir}/man1
install man/*.1 %{buildroot}%{_mandir}/man1/

mkdir -p %{buildroot}%{_unitdir}
install -m 644 files/fail2ban.service %{buildroot}%{_unitdir}/%{name}.service
install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-fail2ban.preset << EOF
enable fail2ban.service
EOF

install -d -m 0755 %{buildroot}%{_var}/run/fail2ban/
install -d -m 0755 %{buildroot}%{_var}/lib/fail2ban/

mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d
install -p -m 0644 files/fail2ban-tmpfiles.conf %{buildroot}%{_sysconfdir}/tmpfiles.d/fail2ban.conf

mkdir -p %{buildroot}%{_sysconfdir}/%{name}/jail.d
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
# Remove test files
rm -r %{buildroot}%{py_sitedir}/%{name}/tests/

%files
%doc ChangeLog README.md TODO
%{_presetdir}/86-fail2ban.preset
%{_unitdir}/%{name}.service
%{_bindir}/%{name}-*
%{_sysconfdir}/tmpfiles.d/fail2ban.conf
%config(noreplace) %{_sysconfdir}/%{name}/jail.d/00-systemd.conf
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/action.d/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/action.d/*.py
%config(noreplace) %{_sysconfdir}/%{name}/filter.d/*.conf
%{_sysconfdir}/%{name}/filter.d/ignorecommands/
%dir %{_var}/run/%{name}
%dir %{_var}/lib/%{name}
%{py_sitedir}/%{name}/*.py
%{py_sitedir}/%{name}/client/*.py*
%{py_sitedir}/%{name}/server/*.py*
%{py_sitedir}/%{name}-%{version}-py%{py_ver}.egg-info
%{_mandir}/man1/*
