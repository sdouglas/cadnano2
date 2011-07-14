%define name CADnano
%define version 1.5
%define unmangled_version 1.5
%define release 1

Summary: DNA Origami Design Software
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: UNKNOWN
Group: Application/Engineering
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Wyss Institute <wyss@wyss.harvard.edu>
Requires: PyQt4
BuildRequires: desktop-file-utils
Url: http://www.cadnano.org/

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
python setup.py install --install-scripts=/usr/local/CADnano

desktop-file-install                                    \
--delete-original                                       \
--dir=%{buildroot}%{_datadir}/applications              \
%{buildroot}/%{_datadir}/cadnano.desktop

%post
/usr/bin/update-mime-database %{_datadir}/mime &>/dev/null || :
/usr/bin/update-desktop-database -q %{_datadir}/applications &>/dev/null || :
/usr/bin/gtk-update-icon-cache -qf %{_datadir}/icons/hicolor &> /dev/null || :

%postun
/usr/bin/update-mime-database %{_datadir}/mime &>/dev/null || :
/usr/bin/update-desktop-database -q %{_datadir}/applications &>/dev/null || :
/usr/bin/gtk-update-icon-cache -qf %{_datadir}/icons/hicolor &> /dev/null || :

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%{_bindir}/cadnano.sh
%{_datadir}/applications/cadnano.desktop
%{_datadir}/icons/hicolor/*/apps/cadnano.png
%{_datadir}/cadnano/
