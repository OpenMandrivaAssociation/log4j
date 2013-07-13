%define gcj_support 0
%define bootstrap 0
%define section        free

Summary:	Java logging package
Name:		log4j
Version:	1.2.14
Release:	13
Group:		Development/Java
License:	Apache License
Url:		http://logging.apache.org/log4j/
Source0:	http://www.apache.org/dist/logging/log4j/%{version}/logging-log4j-%{version}.tar.gz
# Converted from src/java/org/apache/log4j/lf5/viewer/images/lf5_small_icon.gif
Source1:	%{name}-logfactor5.png
Source2:	%{name}-logfactor5.sh
Source3:	%{name}-logfactor5.desktop
# Converted from docs/images/logo.jpg
Source4:	%{name}-chainsaw.png
Source5:	%{name}-chainsaw.sh
Source6:	%{name}-chainsaw.desktop
Source7:	%{name}.catalog
Patch0:		%{name}-logfactor5-userdir.patch
Patch1:		%{name}-javadoc-xlink.patch

%if %{gcj_support}
BuildRequires:	gcc-java
BuildRequires:	java-gcj-compat-devel
%else
BuildArch:	noarch
%endif
BuildRequires:	ant
BuildRequires:	java-rpmbuild >= 0:1.5
BuildRequires:	jaf >= 0:1.0.1
%if !%{bootstrap}
BuildRequires:	javamail >= 0:1.2
%endif
BuildRequires:	java-javadoc
BuildRequires:	jms
BuildRequires:	jndi
BuildRequires:	mx4j
Requires:	jpackage-utils >= 0:1.5
Requires:	liblog4j-java = %{version}
Requires:	java >= 0:1.6.0
# TODO:	check if we could conditionalize these in %post and remove these:
Requires(post):	sgml-common libxml2-utils
Requires(preun):	libxml2-utils
Requires(postun):	sgml-common

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
Summary:	Manual for %{name}
Group:		Development/Java

%description    manual
Documentation for %{name}.

%package        javadoc
Summary:	Javadoc for %{name}
Group:		Development/Java

%description    javadoc
Javadoc for %{name}.

%prep
%setup -qn logging-%{name}-%{version}
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

%ant \
	-Djdk.javadoc=%{_javadocdir}/java \
	-Djavac.source=1.3 jar javadoc
if [ -z "`unzip -l dist/lib/%{name}-%{version}.jar |grep META-INF/INDEX.LIST`" ]; then
	%jar -i dist/lib/%{name}-%{version}.jar
fi

%install
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
%doc INSTALL LICENSE
%{_bindir}/*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/sgml/%{name}

%files -n liblog4j-java
%{_javadir}/*.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*.jar.*
%endif

%files manual
%doc docs/* contribs

%files javadoc
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*
%{_javadocdir}/%{name}

