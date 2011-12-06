#
# $Id: sfcb.spec.in,v 1.16 2007/03/16 13:54:44 mihajlov Exp $
#
# Package spec for sblim-sfcb
#

Name: sblim-sfcb
Summary: Small Footprint CIM Broker
URL: http://www.sblim.org
Version: 1.3.8
Release: 1%{?dist}
Group: Applications/System
License: EPL
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
Source0: http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2
Patch0:	sblim-sfcb-disable_auto_service_start.patch
Patch1: sblim-sfcb-1.3.7-initscript.patch
#Patch2: accepted by upstream
Patch2: sblim-sfcb-1.3.7-close_logging.patch
Provides: cim-server
Requires: cim-schema
Requires: util-linux-ng
Requires(post): chkconfig
Requires(preun): chkconfig
BuildRequires: libcurl-devel
BuildRequires: zlib-devel
BuildRequires: openssl-devel
BuildRequires: pam-devel
BuildRequires: cim-schema
BuildRequires: bison flex

%Description
Small Footprint CIM Broker (sfcb) is a CIM server conforming to the
CIM Operations over HTTP protocol.
It is robust, with low resource consumption and therefore specifically 
suited for embedded and resource constrained environments.
sfcb supports providers written against the Common Manageability
Programming Interface (CMPI).

#%package devel
#Summary:	Sblim-sfcb Development Files
#Group:		Development/Libraries
#Requires:	%{name} = %{version}-%{release}
#%description devel
#Sblim-sfcb Development Files

%prep
%setup -q -T -b 0 -n %{name}-%{version}
%patch0 -p1 -b .disable_auto_service_start
%patch1 -p1 -b .initscript
%patch2 -p1 -b .close_logging

%build
%configure --enable-debug --enable-ssl --enable-pam --enable-ipv6 CFLAGS="$CFLAGS -D_GNU_SOURCE"
 
make 

%install
rm -rf $RPM_BUILD_ROOT 

make DESTDIR=$RPM_BUILD_ROOT install
mkdir -p $RPM_BUILD_ROOT/%{_initddir}
mv $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/sfcb $RPM_BUILD_ROOT/%{_initddir}/sblim-sfcb
sed -i -e 's/\/var\/lock\/subsys\/sfcb/\/var\/lock\/subsys\/sblim-sfcb/g' $RPM_BUILD_ROOT/%{_initddir}/sblim-sfcb
# remove unused static libraries and so files
rm -f $RPM_BUILD_ROOT/%{_libdir}/sfcb/*.la
#rm -f $RPM_BUILD_ROOT/%{_libdir}/sfcb/*.so

echo "%defattr(-,root,root,-)" > _pkg_list

find $RPM_BUILD_ROOT/%{_datadir}/sfcb -type f | grep -v $RPM_BUILD_ROOT/%{_datadir}/sfcb/CIM >> _pkg_list
sed -i s?$RPM_BUILD_ROOT??g _pkg_list > _pkg_list_2
#mv -f _pkg_list_2 _pkg_list
echo "%config(noreplace) %{_sysconfdir}/sfcb/*" >> _pkg_list
echo "%config(noreplace) %{_sysconfdir}/pam.d/*" >> _pkg_list
echo "%doc %{_datadir}/doc/*" >> _pkg_list
echo "%{_datadir}/man/man1/*" >> _pkg_list
echo "%{_initddir}/sblim-sfcb" >> _pkg_list
echo "%{_localstatedir}/lib/sfcb" >> _pkg_list
echo "%{_bindir}/*" >> _pkg_list
echo "%{_sbindir}/*" >> _pkg_list
echo "%{_libdir}/sfcb/*.so.*" >> _pkg_list
echo "%{_libdir}/sfcb/*.so" >> _pkg_list
#echo "%{_libdir}/sfcb/*.la" >> _pkg_list

cat _pkg_list

%clean
rm -rf $RPM_BUILD_ROOT 

%post 
%{_datadir}/sfcb/genSslCert.sh %{_sysconfdir}/sfcb &>/dev/null || :
/sbin/ldconfig
%{_bindir}/sfcbrepos -f -c /usr/share/mof/cim-current
/sbin/chkconfig --add sblim-sfcb

%preun
if [ $1 = 0 ]; then
	/sbin/service sblim-sfcb stop&>/dev/null
	/sbin/chkconfig	--del	sblim-sfcb
fi

%postun
/sbin/ldconfig
if [ $1 -gt 1 ]; then
	/sbin/service sblim-sfcb condrestart|try-restart &> /dev/null
fi

%files -f _pkg_list

#%files devel
#%defattr(-,root,root)
##%{_includedir}/*
#%{_libdir}/sfcb/*.so*
#%{_libdir}/sfcb/*.la
#%doc COPYING README

%changelog
* Mon Jun 21 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.3.8-1
- Update to sblim-1.3.8

* Wed May 26 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.3.7-6
- Fix clone of return value
- Fix Requires

* Wed May 12 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.3.7-5
- Add missing soname files, fix unmatched calls of closeLogging()
  and startLogging()

* Thu Apr 22 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.3.7-4
- Fix initscript

* Thu Mar 18 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.3.7-3
- Make sblim-sfcb post install scriptlet silent

* Mon Mar 15 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.3.7-2
- Fix value.c

* Thu Mar 11 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.3.7-1
- Update to sblim-sfcb-1.3.7

* Mon Mar  1 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.3.4-10
- Fix dist tag in Release field

* Wed Nov 25 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.3.4-9.1
- Bump for rebuild

* Wed Sep 30 2009 <praveen_paladugu@dell.com>- 1.3.4-9
- LocalInterfaceInvokeMethodFix: CHARS and string were handled the same.
-  They are differentiated in this patch.
- destroyThreadKey: Local sfcb connect was creating thread specific data
-  associating a key to it. This won't get deleted resulting in crash
-  of opwsman, sfcc and sfcb. This patch deletes that data.

* Tue Sep 22 2009 <srinivas_ramanatha@dell.com> - 1.3.4-8
- Removed the devel package and moved the init script to right directory

* Wed Sep 16 2009 <srinivas_ramanatha@dell.com> - 1.3.4-7
- Modified the spec based on Praveen's comments

* Thu Sep 10 2009 <srinivas_ramanatha@dell.com> - 1.3.4-6
- Fixed the incoherent init script problem by renaming the init script

* Thu Sep 03 2009 <srinivas_ramanatha@dell.com> - 1.3.4-5
- added the devel package to fit in all the development files 
- Made changes to the initscript not to start the service by default

* Thu Jul 02 2009 <ratliff@austin.ibm.com> - 1.3.4-4
- added build requires for flex, bison, cim-schema suggested by Sean Swehla
- added sfcbrepos directive to post section

* Thu Jun 18 2009 <ratliff@austin.ibm.com> - 1.3.4-3
- re-ordered the top so that the name comes first
- added the la files to the package list
- removed the smp flags from make because that causes a build break
- updated spec file to remove schema and require the cim-schema package
- change provides statement to cim-server as suggested by Matt Domsch
- updated to upstream version 1.3.4 which was released Jun 15 2009

* Thu Oct 09 2008 <ratliff@austin.ibm.com> - 1.3.2-2
- updated spec file based on comments from Srini Ramanatha as below:
- updated the Release line to add dist to be consistent with sblim-sfcc
- updated the source URL

* Wed Oct 08 2008 <ratliff@austin.ibm.com> - 1.3.2-1
- updated upstream version and added CFLAGS to configure to work 
- around http://sources.redhat.com/bugzilla/show_bug.cgi?id=6545

* Fri Aug 08 2008 <ratliff@austin.ibm.com> - 1.3.0-1
- updated buildrequires to require libcurl-devel rather than curl-devel
- removed requires to allow rpm to automatically generate the requires
- removed echo to stdout
- removed paranoia check around cleaning BuildRoot per Fedora MUST requirements
- changed group to supress rpmlint complaint
- added chkconfig to enable sfcb by default when it is installed
- added patch0 to enable 1.3.0 to build on Fedora 9

* Fri Feb 09 2007  <mihajlov@dyn-9-152-143-45.boeblingen.de.ibm.com> - 1.2.1-0
- Updated for 1.2.1 content, enabled SSL, indications

* Wed Aug 31 2005  <mihajlov@dyn-9-152-143-45.boeblingen.de.ibm.com> - 0.9.0b-0
- Support for man pages added
