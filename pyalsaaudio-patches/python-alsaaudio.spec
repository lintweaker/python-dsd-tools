%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:		python-alsaaudio
Version:	0.7
Release:	8%{?dist}
Summary:	Python Alsa Bindings

Group:		Development/Languages
License:	Python
URL:		http://sourceforge.net/projects/pyalsaaudio
Source0:	http://downloads.sourceforge.net/pyalsaaudio/pyalsaaudio-%{version}.tar.gz
Patch0:		pyalsaaudio-add-dsd-formats.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	python-devel
BuildRequires:	alsa-lib-devel


%description
The Python-AlsaAudio package contains bindings for the ALSA sound API.


%prep
%setup -q -n pyalsaaudio-%{version}
%patch0 -p1

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc CHANGES LICENSE README TODO
%{python_sitearch}/*


%changelog
* Mon Sep 10 2014 Jurgen Kramer <gtmkramer@gmail.com> - 0.7-8
- Add DSD sample formats

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Sep 08 2011 Nicolas Chauvet <kwizart@gmail.com> - 0.7-1
- Update to 0.7

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.6-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Sat Jan 30 2010 Nicolas Chauvet <kwizart@fedoraproject.org> - 0.6-1
- Update to 0.6

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed May  6 2009 kwizart < kwizart at gmail.com > - 0.5-1
- Update to 0.5

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Feb 12 2009 kwizart < kwizart at gmail.com > - 0.4-1
- Update to 0.4

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.3-3
- Rebuild for Python 2.6

* Fri Oct 17 2008 kwizart < kwizart at gmail.com > - 0.3-2
- Rebuild for F-10

* Tue Feb 19 2008 kwizart < kwizart at gmail.com > - 0.3-1
- Update to 0.3

* Sat Feb  9 2008 kwizart < kwizart at gmail.com > - 0.2-3
- Rebuild for gcc43

* Fri Dec  8 2006 Brian Pepple <bpepple@fedoraproject.org> - 0.2-2
- Rebuild against new python.

* Thu Nov  2 2006 Brian Pepple <bpepple@fedoraproject.org> - 0.2-1
- Initial FE spec.

