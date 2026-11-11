Name:		log4j
Version:	2.26.1
Release:	1
Summary:	Apache Log4j API
Group:		Development/Java
License:	Apache-2.0
URL:		https://logging.apache.org/log4j/2.x/
# Tag rel/2.26.1. Two test-only .class files are removed from this archive.
# This build is the API jar. log4j-core is not compiled here.
Source0:	https://github.com/apache/logging-log4j2/archive/refs/tags/rel/%{version}.tar.gz#/log4j-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(org.osgi:osgi.core)
BuildRequires:	mvn(org.jspecify:jspecify)
BuildRequires:	mvn(com.google.errorprone:error_prone_annotations)

%description
Apache Log4j API 2.26.1. Gradle 9.9.1 accepts log4j-core
at this version, and that jar depends on this API.
The core, plus Kafka, ZeroMQ, and JMS appenders, is not
compiled in this build.

%prep
%autosetup -n logging-log4j2-rel-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
# CLASS-retention markers. Not installed. bnd and the OSGi annotation
# jars are not in cooker. osgi.core is.
mkdir -p bnd-src/aQute/bnd/annotation/spi bnd-src/org/osgi/annotation/bundle bnd-src/org/osgi/annotation/versioning
cat > bnd-src/aQute/bnd/annotation/Resolution.java <<'EOF'
package aQute.bnd.annotation;
public enum Resolution { MANDATORY, OPTIONAL }
EOF
cat > bnd-src/aQute/bnd/annotation/Cardinality.java <<'EOF'
package aQute.bnd.annotation;
public enum Cardinality { SINGLE, MULTIPLE }
EOF
cat > bnd-src/aQute/bnd/annotation/spi/ServiceProvider.java <<'EOF'
package aQute.bnd.annotation.spi;
import aQute.bnd.annotation.Resolution;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Retention(RetentionPolicy.CLASS)
@Target(ElementType.TYPE)
public @interface ServiceProvider {
	Class<?> value();
	Resolution resolution() default Resolution.MANDATORY;
}
EOF
cat > bnd-src/aQute/bnd/annotation/spi/ServiceConsumer.java <<'EOF'
package aQute.bnd.annotation.spi;
import aQute.bnd.annotation.Cardinality;
import aQute.bnd.annotation.Resolution;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Retention(RetentionPolicy.CLASS)
@Target(ElementType.TYPE)
public @interface ServiceConsumer {
	Class<?> value();
	Resolution resolution() default Resolution.MANDATORY;
	Cardinality cardinality() default Cardinality.SINGLE;
}
EOF
cat > bnd-src/org/osgi/annotation/bundle/Export.java <<'EOF'
package org.osgi.annotation.bundle;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Retention(RetentionPolicy.CLASS)
@Target(ElementType.PACKAGE)
public @interface Export {}
EOF
cat > bnd-src/org/osgi/annotation/bundle/Header.java <<'EOF'
package org.osgi.annotation.bundle;
import java.lang.annotation.ElementType;
import java.lang.annotation.Repeatable;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Retention(RetentionPolicy.CLASS)
@Target(ElementType.TYPE)
@Repeatable(Header.Headers.class)
public @interface Header {
	String name();
	String value();
	@Retention(RetentionPolicy.CLASS)
	@Target(ElementType.TYPE)
	@interface Headers { Header[] value(); }
}
EOF
cat > bnd-src/org/osgi/annotation/versioning/Version.java <<'EOF'
package org.osgi.annotation.versioning;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Retention(RetentionPolicy.CLASS)
@Target(ElementType.PACKAGE)
public @interface Version {
	String value();
}
EOF
mkdir -p bnd-classes
javac --release 8 -encoding UTF-8 -Xlint:-options -d bnd-classes \
	bnd-src/aQute/bnd/annotation/Resolution.java \
	bnd-src/aQute/bnd/annotation/Cardinality.java \
	bnd-src/aQute/bnd/annotation/spi/ServiceProvider.java \
	bnd-src/aQute/bnd/annotation/spi/ServiceConsumer.java \
	bnd-src/org/osgi/annotation/bundle/Export.java \
	bnd-src/org/osgi/annotation/bundle/Header.java \
	bnd-src/org/osgi/annotation/versioning/Version.java
jar cf bnd-ann.jar -C bnd-classes .

mkdir -p classes
find log4j-api/src/main/java -name '*.java' ! -name module-info.java > sources.list
test "$(wc -l < sources.list)" -eq 150
javac --release 8 -encoding UTF-8 -Xlint:-options \
	-cp "bnd-ann.jar:%{_javadir}/osgi-core.jar:%{_javadir}/jspecify.jar:%{_javadir}/error_prone_annotations.jar" \
	-d classes @sources.list
/bin/cp -a log4j-api/src/main/resources/. classes/
jar cf log4j-api.jar -C classes .
cat > log4j-api.pom <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.apache.logging.log4j</groupId>
  <artifactId>log4j-api</artifactId>
  <version>2.26.1</version>
  <name>Apache Log4j API</name>
  <description>Apache Log4j API.</description>
  <url>https://logging.apache.org/log4j/2.x/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.core</artifactId>
      <version>6.0.0</version>
      <optional>true</optional>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact log4j-api.pom:log4j-api.jar \
	--file-name log4j-api \
	--filelist .mfiles

%check
JAR=%{buildroot}%{_javadir}/log4j-api.jar
test -f "$JAR"
mkdir -p check
cat > check/Smoke.java <<'END'
import org.apache.logging.log4j.message.SimpleMessage;
public class Smoke {
	public static void main(String[] args) {
		System.out.println(new SimpleMessage("log4japi_ok").getFormattedMessage());
	}
}
END
javac --release 8 -encoding UTF-8 -Xlint:-options -cp "$JAR" -d check check/Smoke.java
java -cp "check:$JAR" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'log4japi_ok' check/out.txt

%files -f .mfiles
%license LICENSE.txt NOTICE.txt
%doc README.adoc
