Name:		log4j
Version:	2.26.1
Release:	2
Summary:	Apache Log4j API and Core
Group:		Development/Java
License:	Apache-2.0
URL:		https://logging.apache.org/log4j/2.x/
# Tag rel/2.26.1. Two test-only .class files are removed from this archive.
Source0:	https://github.com/apache/logging-log4j2/archive/refs/tags/rel/%{version}.tar.gz#/log4j-%{version}.tar.gz
# Drop the Disruptor 3.x event-handler shim. Cooker ships Disruptor 4.0.0,
# and the 4.x handlers in this tree are the ones AsyncLogger uses.
Patch0:		log4j-2.26.1-disruptor4.patch

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(org.osgi:osgi.core)
BuildRequires:	mvn(org.jspecify:jspecify)
BuildRequires:	mvn(com.google.errorprone:error_prone_annotations)
BuildRequires:	mvn(org.apache.commons:commons-compress)
BuildRequires:	mvn(org.apache.commons:commons-csv)
BuildRequires:	mvn(org.apache.commons:commons-lang3)
BuildRequires:	mvn(com.lmax:disruptor)
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-core)
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-annotations)
BuildRequires:	mvn(com.fasterxml.jackson.core:jackson-databind)
BuildRequires:	mvn(com.fasterxml.jackson.dataformat:jackson-dataformat-xml)
BuildRequires:	mvn(com.fasterxml.jackson.dataformat:jackson-dataformat-yaml)
BuildRequires:	mvn(org.jctools:jctools-core)
BuildRequires:	mvn(org.codehaus.woodstox:stax2-api)
BuildRequires:	mvn(com.fasterxml.woodstox:woodstox-core)
BuildRequires:	mvn(javax.activation:javax.activation-api)
BuildRequires:	mvn(com.sun.mail:javax.mail)
BuildRequires:	mvn(javax.jms:javax.jms-api)

%description
Apache Log4j 2.26.1 API and Core. Gradle 9.9.1 accepts
log4j-core at this version. Kafka, JeroMQ, and the Conversant
Disruptor queue are not compiled. Async loggers use the Disruptor
4.0.0 handlers.

%prep
%autosetup -n logging-log4j2-rel-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
set -eo pipefail
# CLASS-retention markers. Not installed. bnd and the OSGi annotation
# jars are not in cooker. osgi.core is.
mkdir -p bnd-src/aQute/bnd/annotation/spi \
	bnd-src/aQute/bnd/annotation/baseline \
	bnd-src/aQute/bnd/annotation/jpms \
	bnd-src/org/osgi/annotation/bundle \
	bnd-src/org/osgi/annotation/versioning
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
cat > bnd-src/aQute/bnd/annotation/baseline/BaselineIgnore.java <<'EOF'
package aQute.bnd.annotation.baseline;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Retention(RetentionPolicy.CLASS)
@Target({ElementType.TYPE, ElementType.PACKAGE, ElementType.METHOD, ElementType.CONSTRUCTOR, ElementType.FIELD})
public @interface BaselineIgnore {
	String value();
}
EOF
cat > bnd-src/aQute/bnd/annotation/jpms/ExportTo.java <<'EOF'
package aQute.bnd.annotation.jpms;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Retention(RetentionPolicy.CLASS)
@Target({ElementType.PACKAGE, ElementType.TYPE})
public @interface ExportTo {
	String[] value();
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
cat > bnd-src/org/osgi/annotation/versioning/ProviderType.java <<'EOF'
package org.osgi.annotation.versioning;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Retention(RetentionPolicy.CLASS)
@Target({ElementType.PACKAGE, ElementType.TYPE})
public @interface ProviderType {}
EOF
mkdir -p bnd-classes
javac --release 8 -encoding UTF-8 -Xlint:-options -d bnd-classes \
	$(find bnd-src -name '*.java')
jar cf bnd-ann.jar -C bnd-classes .

mkdir -p classes
find log4j-api/src/main/java -name '*.java' ! -name module-info.java > sources.list
test "$(wc -l < sources.list)" -eq 150
javac --release 8 -encoding UTF-8 -Xlint:-options \
	-cp "bnd-ann.jar:%{_javadir}/osgi-core.jar:%{_javadir}/jspecify.jar:%{_javadir}/error_prone_annotations.jar" \
	-d classes @sources.list
/bin/cp -a log4j-api/src/main/resources/. classes/
jar cf log4j-api.jar -C classes .
jar i log4j-api.jar
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

# Kafka, JeroMQ, and Conversant are optional appenders whose libraries are
# not in cooker. RingBufferLogEventHandler is the Disruptor 3.x shim.
mkdir -p core-classes
find log4j-core/src/main/java -name '*.java' ! -name module-info.java \
	! -path '*/appender/mom/kafka/*' \
	! -path '*/appender/mom/jeromq/*' \
	! -name DisruptorBlockingQueueFactory.java \
	! -name RingBufferLogEventHandler.java > core-sources.list
test "$(wc -l < core-sources.list)" -eq 731
CORECP="bnd-ann.jar:log4j-api.jar:%{_javadir}/osgi-core.jar:%{_javadir}/jspecify.jar:%{_javadir}/jackson-core.jar:%{_javadir}/jackson-annotations.jar:%{_javadir}/jackson-databind.jar:%{_javadir}/jackson-dataformat-xml.jar:%{_javadir}/jackson-dataformat-yaml.jar:%{_javadir}/commons-compress.jar:%{_javadir}/commons-csv.jar:%{_javadir}/commons-lang3.jar:%{_javadir}/disruptor.jar:%{_javadir}/jctools-core.jar:%{_javadir}/stax2-api.jar:%{_javadir}/woodstox-core.jar:%{_javadir}/javax.activation-api.jar:%{_javadir}/java.mail.jar:%{_javadir}/javax.jms-api.jar"
javac --release 8 -encoding UTF-8 -Xlint:-options -cp "$CORECP" -d core-classes @core-sources.list
/bin/cp -a log4j-core/src/main/resources/. core-classes/
javac -proc:only \
	-processor org.apache.logging.log4j.core.config.plugins.processor.PluginProcessor \
	--release 8 -encoding UTF-8 -Xlint:-options \
	-processorpath "core-classes:$CORECP" -classpath "core-classes:$CORECP" \
	-d core-classes @core-sources.list
test -s core-classes/META-INF/org/apache/logging/log4j/core/config/plugins/Log4j2Plugins.dat
mkdir -p core-classes/META-INF/services
printf '%s\n' org.apache.logging.log4j.core.impl.Log4jProvider \
	> core-classes/META-INF/services/org.apache.logging.log4j.spi.Provider
printf '%s\n' org.apache.logging.log4j.core.impl.ThreadContextDataProvider \
	> core-classes/META-INF/services/org.apache.logging.log4j.core.util.ContextDataProvider
printf '%s\n' org.apache.logging.log4j.core.message.ExtendedThreadInfoFactory \
	> 'core-classes/META-INF/services/org.apache.logging.log4j.message.ThreadDumpMessage$ThreadInfoFactory'
cat > core-manifest.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: org.apache.logging.log4j.core

EOF
jar cfm log4j-core.jar core-manifest.mf -C core-classes .
jar i log4j-core.jar
javap -verbose -cp log4j-core.jar org.apache.logging.log4j.core.Logger | grep -F 'major version: 52'
jar --describe-module --file log4j-core.jar > core-describe.txt
if grep -F -q 'Unable to derive' core-describe.txt; then
	cat core-describe.txt
	exit 1
fi
cat > log4j-core.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.apache.logging.log4j</groupId>
  <artifactId>log4j-core</artifactId>
  <version>2.26.1</version>
  <name>Apache Log4j Core</name>
  <description>Apache Log4j implementation.</description>
  <url>https://logging.apache.org/log4j/2.x/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-api</artifactId>
      <version>2.26.1</version>
    </dependency>
    <dependency>
      <groupId>org.apache.commons</groupId>
      <artifactId>commons-compress</artifactId>
      <version>1.28.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>org.apache.commons</groupId>
      <artifactId>commons-csv</artifactId>
      <version>1.14.1</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>org.apache.commons</groupId>
      <artifactId>commons-lang3</artifactId>
      <version>3.21.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.lmax</groupId>
      <artifactId>disruptor</artifactId>
      <version>4.0.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-core</artifactId>
      <version>2.23.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-annotations</artifactId>
      <version>2.23</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.23.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.dataformat</groupId>
      <artifactId>jackson-dataformat-xml</artifactId>
      <version>2.23.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.dataformat</groupId>
      <artifactId>jackson-dataformat-yaml</artifactId>
      <version>2.23.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>org.jctools</groupId>
      <artifactId>jctools-core</artifactId>
      <version>4.0.7</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>org.codehaus.woodstox</groupId>
      <artifactId>stax2-api</artifactId>
      <version>4.3.2</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>javax.activation</groupId>
      <artifactId>javax.activation-api</artifactId>
      <version>1.2.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.sun.mail</groupId>
      <artifactId>javax.mail</artifactId>
      <version>1.6.2</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>javax.jms</groupId>
      <artifactId>javax.jms-api</artifactId>
      <version>2.0.1</version>
      <optional>true</optional>
    </dependency>
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
sysjar install --buildroot %{buildroot} \
	--artifact log4j-core.pom:log4j-core.jar \
	--file-name log4j-core \
	--filelist .mfiles-core
while IFS= read -r line; do
	grep -qxF "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
done < .mfiles-core

%check
set -eo pipefail
API=%{buildroot}%{_javadir}/log4j-api.jar
CORE=%{buildroot}%{_javadir}/log4j-core.jar
test -f "$API"
test -f "$CORE"
mkdir -p check
cat > check/ApiSmoke.java <<'END'
import org.apache.logging.log4j.message.SimpleMessage;
public class ApiSmoke {
	public static void main(String[] args) {
		System.out.println(new SimpleMessage("log4japi_ok").getFormattedMessage());
	}
}
END
javac --release 8 -encoding UTF-8 -Xlint:-options -cp "$API" -d check check/ApiSmoke.java
java -cp "check:$API" ApiSmoke > check/api.txt
cat check/api.txt
grep -F -q 'log4japi_ok' check/api.txt
cat > check/CoreSmoke.java << 'END'
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.core.config.Configurator;
import org.apache.logging.log4j.core.config.builder.api.ConfigurationBuilder;
import org.apache.logging.log4j.core.config.builder.api.ConfigurationBuilderFactory;
import org.apache.logging.log4j.core.config.builder.impl.BuiltConfiguration;
public class CoreSmoke {
	public static void main(String[] args) {
		ConfigurationBuilder<BuiltConfiguration> builder = ConfigurationBuilderFactory.newConfigurationBuilder();
		builder.setStatusLevel(Level.ERROR);
		builder.setConfigurationName("smoke");
		builder.add(builder.newAppender("out", "Console").addAttribute("target", "SYSTEM_OUT"));
		builder.add(builder.newRootLogger(Level.INFO).add(builder.newAppenderRef("out")));
		Configurator.initialize(builder.build());
		Logger log = LogManager.getLogger("gradle");
		log.info("log4jcore_ok");
		System.out.println("logger " + log.getClass().getName());
	}
}
END
CORECP="$CORE:$API:%{_javadir}/disruptor.jar:%{_javadir}/osgi-core.jar:%{_javadir}/jspecify.jar"
javac --release 8 -encoding UTF-8 -Xlint:-options -cp "$CORECP" -d check check/CoreSmoke.java
java -cp "check:$CORECP" CoreSmoke > check/core.txt
cat check/core.txt
grep -F -q 'log4jcore_ok' check/core.txt
grep -F -q 'org.apache.logging.log4j.core.Logger' check/core.txt

%files -f .mfiles
%license LICENSE.txt NOTICE.txt
%doc README.adoc
