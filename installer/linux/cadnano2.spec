Summary: DNA origami design software
Name: CADnano2
Version: 1.5.0
Release: 1%{dist}
License: MIT
Group: 
Source0: %_specdir/cadnano2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
URL: http://www.cadnano.org/
ExcludeArch:
BuildRequires: qt
BuildRequires: pyqt

%description
CADnano 2 is a DNA design software package

%prep
%setup -q
%build
%configure

%install
rm -rf %{buildroot}

python install.py %{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc

%changelog