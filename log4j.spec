%define gcj_support 0
%define bootstrap 0
%define section        free

Name:           log4j
Version:        1.2.14
Release:        %mkrel 12.0.6
Epoch:          0
Summary:        Java logging package
License:        Apache License
URL:            http://logging.apache.org/log4j/
Source0:        http://www.apache.org/dist/logging/log4j/%{version}/logging-log4j-%{version}.tar.gz
# Converted from src/java/org/apache/log4j/lf5/viewer/images/lf5_small_icon.gif
Source1:        %{name}-logfactor5.png
Source2:        %{name}-logfactor5.sh
Source3:        %{name}-logfactor5.desktop
# Converted from docs/images/logo.jpg
Source4:        %{name}-chainsaw.png
Source5:        %{name}-chainsaw.sh
Source6:        %{name}-chainsaw.desktop
Source7:        %{name}.catalog
Patch0:         %{name}-logfactor5-userdir.patch
Patch1:         %{name}-javadoc-xlink.patch
BuildRequires:  java-rpmbuild >= 0:1.5
BuildRequires:  ant
BuildRequires:  jaf >= 0:1.0.1
%if !%{bootstrap}
BuildRequires:  javamail >= 0:1.2
%endif
BuildRequires:  jms
BuildRequires:  mx4j
BuildRequires:  jndi
BuildRequires:  java-javadoc
# (anssi) do not require these explicitely at runtime, they are not needed
# by all apps that use log4j
#Requires:       jaf
#%if !%{bootstrap}
#Requires:       javamail
#%endif
#Requires:       jms
#Requires:       mx4j
# (anssi) jndi is provided by all our Java VMs, so we simplify the dependency
# graph by not requiring it.
#Requires:       jndi
Requires:       jpackage-utils >= 0:1.5
Requires:	liblog4j-java = %{version}
Requires:       java >= 0:1.6.0
# TODO: check if we could conditionalize these in %post and remove these:
Requires(post):	sgml-common libxml2-utils
Requires(preun):	libxml2-utils
Requires(postun):	sgml-common
Group:          Development/Java
%if %{gcj_support}
BuildRequires:        gcc-java
BuildRequires:        java-gcj-compat-devel
%else
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
#Vendor:         JPackage Project
#Distribution:   JPackage

%description
Log4j is a tool to help the programmer output log statements to a
variety of output targets.

# Split to avoid dependency on sgml-common/libxml2-utils in vuze-console package:
%package -n	liblog4j-java
Summary:	Java logging library
Group:		Development/Java
Conflicts:	log4j < 1.2.14-12.0.4

%description -n	liblog4j-java
Log4j is a tool to help the programmer output log statements to a
variety of output targets.

This package contains the jar only. See %{name} for tools and catalogs.

%package        manual
Summary:        Manual for %{name}
Group:          Development/Java

%description    manual
Documentation for %{name}.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description    javadoc
Javadoc for %{name}.

%prep
%setup -q -n logging-%{name}-%{version}
%patch0 -p0
%patch1 -p0
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
# fix perl location
sed -i -e 's|/opt/perl5/bin/perl|%{__perl}|' contribs/KitchingSimon/udpserver.pl

%build
%if !%{bootstrap}
export CLASSPATH=$(build-classpath jaf javamail/mailapi jms mx4j)
%else
export CLASSPATH=$(build-classpath jaf javamail/mailapi)
%endif

%ant -Djdk.javadoc=%{_javadocdir}/java -Djavac.source=1.3 jar javadoc
if [ -z "`unzip -l dist/lib/%{name}-%{version}.jar |grep META-INF/INDEX.LIST`" ]; then
	%jar -i dist/lib/%{name}-%{version}.jar
fi

%install
rm -rf %{buildroot}

# jars
install -m644 dist/lib/%{name}-%{version}.jar -D %{buildroot}%{_javadir}/%{name}-%{version}.jar
ln -s %{name}-%{version}.jar %{buildroot}%{_javadir}/%{name}.jar

# javadoc
install -d %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -r docs/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

# scripts
install -m755 %{SOURCE2} -D %{buildroot}%{_bindir}/logfactor5
install -m755 %{SOURCE5} -D %{buildroot}%{_bindir}/chainsaw

# freedesktop.org menu entries and icons
install -m644 %{SOURCE1} -D %{buildroot}%{_datadir}/pixmaps/logfactor5.png
install -m644 %{SOURCE3} -D %{buildroot}%{_datadir}/applications/jpackage-logfactor5.desktop
install -m644 %{SOURCE4} -D %{buildroot}%{_datadir}/pixmaps/chainsaw.png
install -m644 %{SOURCE6} -D %{buildroot}%{_datadir}/applications/jpackage-chainsaw.desktop

# DTD and the SGML catalog (XML catalog handled in scriptlets)
install -m644 src/java/org/apache/log4j/xml/log4j.dtd -D %{buildroot}%{_datadir}/sgml/%{name}/log4j.dtd
install -m644 %{SOURCE7} -D %{buildroot}%{_datadir}/sgml/%{name}/catalog

%if %{gcj_support}
aot-compile-rpm
%endif

%clean
rm -rf %{buildroot}

%post
%{_bindir}/install-catalog --add \
	%{_sysconfdir}/sgml/%{name}-%{version}-%{release}.cat \
	%{_datadir}/sgml/%{name}/catalog >/dev/null 2>&1

%{_bindir}/xmlcatalog --noout --add system log4j.dtd \
	file://%{_datadir}/sgml/%{name}/log4j.dtd %{_sysconfdir}/xml/catalog >/dev/null 2>&1

%if %{gcj_support}
%post -n liblog4j-java
%update_gcjdb
%endif

%preun
%{_bindir}/xmlcatalog --noout --del \
	log4j.dtd %{_sysconfdir}/xml/catalog >/dev/null 2>&1

%postun
%{_bindir}/install-catalog --remove \
	%{_sysconfdir}/sgml/%{name}-%{version}-%{release}.cat \
	%{_datadir}/sgml/%{name}/catalog >/dev/null 2>&1


%if %{gcj_support}
%postun -n liblog4j-java
%clean_gcjdb
%endif

%files
%defattr(0644,root,root,0755)
%doc INSTALL LICENSE
%attr(0755,root,root) %{_bindir}/*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/sgml/%{name}

%files -n liblog4j-java
%defattr(-,root,root)
%{_javadir}/*.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*.jar.*
%endif

%files manual
%defattr(0644,root,root,0755)
%doc docs/* contribs

%files javadoc
%defattr(0644,root,root,0755)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*
%{_javadocdir}/%{name}


%changelog
* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.2.14-12.0.6mdv2011.0
+ Revision: 606417
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.2.14-12.0.5mdv2010.1
+ Revision: 523192
- rebuilt for 2010.1

* Wed Aug 19 2009 Anssi Hannula <anssi@mandriva.org> 0:1.2.14-12.0.4mdv2010.0
+ Revision: 417912
- split jar to liblog4j-java to reduce vuze-console dependencies

* Tue Aug 18 2009 Jaroslav Tulach <jtulach@mandriva.org> 0:1.2.14-12.0.3mdv2010.0
+ Revision: 417720
- Simplifying dependencies. Requiring java 1.6 and removing special dependencies on various XML tools as they are part of java 1.6 already

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 0:1.2.14-12.0.2mdv2009.1
+ Revision: 351536
- rebuild

* Tue Mar 04 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:1.2.14-12.0.1mdv2008.1
+ Revision: 179040
- BR java-gcj-compat-devel

  + Oden Eriksson <oeriksson@mandriva.com>
    - rebuild

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild
    - rebuild
    - kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Anssi Hannula <anssi@mandriva.org>
    - buildrequire java-rpmbuild, i.e. build with icedtea on x86(_64)

* Sun Sep 16 2007 Anssi Hannula <anssi@mandriva.org> 0:1.2.14-8mdv2008.0
+ Revision: 87965
- remove some bloated runtime requires
- requires java
- use macros for rebuild-gcj-db

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 0:1.2.14-7mdv2008.0
+ Revision: 87202
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

* Thu Sep 13 2007 Nicolas Lécureuil <nlecureuil@mandriva.com> 0:1.2.14-6mdv2008.0
+ Revision: 85360
- Fix validation errors on desktop files

* Mon Sep 10 2007 David Walluck <walluck@mandriva.org> 0:1.2.14-5mdv2008.0
+ Revision: 84029
- silence post scripts
- more strict permissions on file list
- own %%{_libdir}/gcj/%%{name}

* Fri Aug 17 2007 Anssi Hannula <anssi@mandriva.org> 0:1.2.14-4mdv2008.0
+ Revision: 65016
- remove requires on jndi as it is provided by all our Java VMs anyway
  (this avoids having urpmi ask which package should be used be installed
  to satisfy "jndi")

* Tue Aug 14 2007 Anssi Hannula <anssi@mandriva.org> 0:1.2.14-3mdv2008.0
+ Revision: 63120
- use %%jar and %%ant
- define javac.source=1.3 instead of 1.1 to allow build with recent
  eclipse
- use xml-commons-jaxp-1.3-apis explicitely instead of the generic
  xml-commons-apis which is provided by multiple packages (see bug #31473)


* Mon Feb 19 2007 Per Øyvind Karlsen <pkarlsen@mandriva.com> 1.2.14-2mdv2007.0
+ Revision: 122852
- cleanups
- don't screw up symlinks
- index jar
- add reguires for scriptlets

* Tue Dec 12 2006 David Walluck <walluck@mandriva.org> 0:1.2.14-1mdv2007.1
+ Revision: 95237
- 1.2.14
- Import log4j

* Sun Jul 23 2006 David Walluck <walluck@mandriva.org> 0:1.2.13-2.1mdv2007.0
- bump release

* Fri Jun 02 2006 David Walluck <walluck@mandriva.org> 0:1.2.13-1.1mdv2007.0
- 1.2.13
- rebuild for libgcj.so.7

* Fri Dec 02 2005 David Walluck <walluck@mandriva.org> 0:1.2.12-1.1mdk
- 1.2.12
- aot-compile

* Sun Nov 06 2005 David Walluck <walluck@mandriva.org> 0:1.2.9-1.3mdk
- enable rmic task

* Tue May 10 2005 David Walluck <walluck@mandriva.org> 0:1.2.9-1.2mdk
- rebuild as non-bootstrap

* Tue May 10 2005 David Walluck <walluck@mandriva.org> 0:1.2.9-1.1mdk
- release

* Wed Apr 27 2005 Ville Skyttä <scop at jpackage.org> - 0:1.2.9-1jpp
- 1.2.9.
- Fix URLs.
- Crosslink with local JDK javadocs.

* Tue Feb 22 2005 David Walluck <david@jpackage.org> 0:1.2.8-9jpp
- own non-versioned javadoc symlink
- fix perl location in contribs script

* Sun Aug 22 2004 Fernando Nasser <fnasser@redhat.com> - 0:1.2.8-8jpp
- Rebuild wit Ant 1.6.2

