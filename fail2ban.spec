%define debug_package %{nil}

%define _python_bytecompile_build %nil

Summary:	Ban IPs that make too many authentication failures
Name:		fail2ban
Version:	1.1.1
Release:	2
License:	GPLv2+
Group:		System/Configuration/Networking
URL:		https://www.fail2ban.org
Source0:	https://github.com/fail2ban/fail2ban/archive/%{version}.tar.gz
Source1:	fail2ban.rpmlintrc
BuildArch:	noarch
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	help2man

Requires:	tcp_wrappers >= 7.6-29
Requires:	nftables
Requires:	python%{pyver}dist(systemd-python)
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
%{_unitdir}/%{name}.socket
%{_bindir}/%{name}-*
%{_tmpfilesdir}/fail2ban.conf
%config(noreplace) %{_sysconfdir}/%{name}/jail.local
%config %{_sysconfdir}/%{name}/jail.d/00-systemd.conf
%config %{_sysconfdir}/%{name}/*.conf
%config %{_sysconfdir}/%{name}/action.d/*.conf
%config %{_sysconfdir}/%{name}/action.d/*.py
%config %{_sysconfdir}/%{name}/filter.d/*.conf
%{_sysconfdir}/%{name}/filter.d/ignorecommands/
%dir %{_sysconfdir}/%{name}/fail2ban.d
%dir %{_sysconfdir}/%{name}/jail.d
%ghost %dir /run/fail2ban
%dir %{_var}/lib/%{name}
%{py_sitedir}/%{name}
%{py_sitedir}/*.egg-info
%doc %{_mandir}/man1/*
%doc %{_mandir}/man5/*

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

# Start from Fedora paths (same log locations today); keep our own file so they can diverge
mv config/paths-fedora.conf config/paths-omv.conf
sed -i -e '1s/^# Fedora$/# OpenMandriva/' config/paths-omv.conf
sed -i -e 's/^before = paths-.*/before = paths-omv.conf/' config/jail.conf

# Default ban actions live in paths-*.conf since 1.1.1; nftables matches Requires
cat >> config/paths-omv.conf <<EOF

# OpenMandriva default ban actions (overridable in jail.local)
banaction = nftables
banaction_allports = nftables[type=allports]
EOF

%build
%py_build

%install
%py_install

# Replace /var/run with /run in installed files
find %{buildroot} -type f -exec sed -i -e 's|/var\(/run/fail2ban\)|\1|g' {} +

install -d %{buildroot}%{_mandir}/man1
install -d %{buildroot}%{_mandir}/man5
install -m 644 man/*.1 %{buildroot}%{_mandir}/man1/
install -m 644 man/*.5 %{buildroot}%{_mandir}/man5/

mkdir -p %{buildroot}%{_unitdir}
sed -e 's,@BINDIR@,%{_bindir},' files/fail2ban.service.in > %{buildroot}%{_unitdir}/%{name}.service
sed -e 's,@BINDIR@,%{_bindir},' files/fail2ban.socket.in > %{buildroot}%{_unitdir}/%{name}.socket
install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-fail2ban.preset << EOF
enable fail2ban.service
EOF

install -d -m 0755 %{buildroot}%{_var}/lib/fail2ban/

mkdir -p %{buildroot}%{_tmpfilesdir}
cat > %{buildroot}%{_tmpfilesdir}/fail2ban.conf <<EOF
D /run/fail2ban 0755 root root -
EOF

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

# remove other distro path configs
rm -f %{buildroot}%{_sysconfdir}/%{name}/paths-{arch,debian,fedora,freebsd,opensuse,osx}.conf

# remove docs
rm -r %{buildroot}%{_docdir}/%{name}
# Remove test files
rm -rf %{buildroot}%{py_sitedir}/%{name}/tests/
rm -f %{buildroot}%{_bindir}/fail2ban-testcases
rm -f %{buildroot}%{_mandir}/man1/fail2ban-testcases.1*
