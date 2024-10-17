%define debug_package %{nil}

%define _python_bytecompile_build %nil

Summary:	Ban IPs that make too many authentication failures
Name:		fail2ban
Version:	1.0.2
Release:	3
License:	GPLv2+
Group:		System/Configuration/Networking
URL:		https://www.fail2ban.org
Source0:	https://github.com/fail2ban/fail2ban/archive/%{version}.tar.gz
Source1:	fail2ban.rpmlintrc
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	help2man

Requires:	python >= 3
Requires:	tcp_wrappers >= 7.6-29
Requires:	nftables
Requires:	python-systemd >= 234
Requires:	whois

%description
Fail2Ban scans log files like /var/log/secure and bans IP that makes
too many password failures. It updates firewall rules to reject the IP
address. These rules can be defined by the user. Fail2Ban can read
multiple log files including sshd or Apache web server logs.

%files
%doc ChangeLog README.md TODO
%{_presetdir}/86-fail2ban.preset
%{_unitdir}/%{name}.service
%{_bindir}/%{name}-*
%{_tmpfilesdir}/fail2ban.conf
%config(noreplace) %{_sysconfdir}/%{name}/jail.local
%config %{_sysconfdir}/%{name}/jail.d/00-systemd.conf
%config %{_sysconfdir}/%{name}/*.conf
%config %{_sysconfdir}/%{name}/action.d/*.conf
%config %{_sysconfdir}/%{name}/action.d/*.py
%config %{_sysconfdir}/%{name}/filter.d/*.conf
%{_sysconfdir}/%{name}/filter.d/ignorecommands/
%dir %{_var}/run/%{name}
%dir %{_var}/lib/%{name}
%{py_sitedir}/%{name}/*.py
%{py_sitedir}/%{name}/client/*.py*
%{py_sitedir}/%{name}/server/*.py*
%{py_sitedir}/*.egg-info
%doc %{_mandir}/man1/*

%package firewalld
Summary:	Firewalld support for Fail2Ban
Requires:	%{name} = %{EVRD}
Requires:	firewalld

%description firewalld
This package enables support for manipulating firewalld rules.

%files firewalld
%config(noreplace) %{_sysconfdir}/fail2ban/jail.d/00-firewalld.conf

#--------------------------------------------------------------------

%prep
%autosetup -p1

%build
./fail2ban-2to3

%py_build

%install
%py_install

# Replace /var/run with /run, but not in the top source directory
find . -mindepth 2 -type f -exec sed -i -e 's|/var\(/run/fail2ban\)|\1|g' {} +

install -d %{buildroot}/%{_mandir}/man1
install man/*.1 %{buildroot}%{_mandir}/man1/

mkdir -p %{buildroot}%{_unitdir}
install -m 644 build/fail2ban.service %{buildroot}%{_unitdir}/%{name}.service
install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-fail2ban.preset << EOF
enable fail2ban.service
EOF

install -d -m 0755 %{buildroot}%{_var}/run/fail2ban/
install -d -m 0755 %{buildroot}%{_var}/lib/fail2ban/

mkdir -p %{buildroot}%{_tmpfilesdir}
install -p -m 0644 files/fail2ban-tmpfiles.conf %{buildroot}%{_tmpfilesdir}/fail2ban.conf

# firewalld configuration
cat > %{buildroot}%{_sysconfdir}/%{name}/jail.d/00-firewalld.conf <<EOF
# This file is part of the fail2ban-firewalld package to configure the use of
# the firewalld actions as the default actions.  You can remove this package
# (along with the empty fail2ban meta-package) if you do not use firewalld
[DEFAULT]
banaction = firewallcmd-rich-rules
banaction_allports = firewallcmd-rich-rules
EOF

# systemd journal configuration
cat > %{buildroot}%{_sysconfdir}/%{name}/jail.d/00-systemd.conf <<EOF
# This file is part of the fail2ban-systemd package to configure the use of
# the systemd journal as the default backend.  You can remove this package
# (along with the empty fail2ban meta-package) if you do not want to use the
# journal backend
[DEFAULT]
backend=systemd
EOF

echo "# Do all your modifications to the jail's configuration in jail.local!" > %{buildroot}%{_sysconfdir}/%{name}/jail.local

# remove non-Linux actions
rm -rf %{buildroot}%{_sysconfdir}/%{name}/action.d/*ipfw.conf
rm -rf %{buildroot}%{_sysconfdir}/%{name}/action.d/{ipfilter,pf,ufw}.conf
rm -rf %{buildroot}%{_sysconfdir}/%{name}/action.d/osx-*.conf

# remove docs
rm -r %{buildroot}%{_docdir}/%{name}
# Remove test files
rm -r %{buildroot}%{py_sitedir}/%{name}/tests/

%post
%systemd_post fail2ban.service

%preun
%systemd_preun fail2ban.service

%postun
%systemd_postun_with_restart fail2ban.service
