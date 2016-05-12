%{?scl:%scl_package jfreechart}
%{!?scl:%global pkg_name %{name}}

# Use java common's requires/provides generator
%{?java_common_find_provides_and_requires}

Name:           %{?scl_prefix}jfreechart
Version:        1.0.14
# Release should be higher than el7 builds. Use convention
# 60.X where X is an increasing int. 60 for rhel-6. We use
# 70.X for rhel-7. For some reason we cannot rely on the
# dist tag.
Release:        60.6%{?dist}
Summary:        Java chart library

Group:          Development/Libraries
License:        LGPLv2+
URL:            http://www.jfree.org/jfreechart/
Source0:        http://download.sourceforge.net/sourceforge/jfreechart/%{pkg_name}-%{version}.tar.gz
Source1:        bnd.properties

BuildRequires:  %{?scl_prefix_java_common}mvn(javax.servlet:servlet-api)
BuildRequires:  %{?scl_prefix}jcommon >= 1.0.17
BuildRequires:  %{?scl_prefix_java_common}ant
BuildRequires:  %{?scl_prefix_java_common}javapackages-local
# Required for converting jars to OSGi bundles
BuildRequires:  %{?scl_prefix_maven}aqute-bnd
Requires:       %{?scl_prefix}jcommon >= 1.0.17

%{?scl:Requires: %scl_runtime}

BuildArch:      noarch
Patch0:         remove_itext_dep.patch

%description
JFreeChart is a free 100% Java chart library that makes it easy for
developers to display professional quality charts in their applications.


%package javadoc
Summary:        Javadocs for %{name}
Group:          Documentation

%description javadoc
This package contains the API documentation for %{name}.


%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%setup -q -n %{pkg_name}-%{version}
# Erase prebuilt files
find \( -name '*.jar' -o -name '*.class' \) -exec rm -f '{}' \;
%patch0
%mvn_file org.jfree:%{pkg_name} %{pkg_name}
%pom_remove_dep xml-apis:xml-apis pom.xml
%{?scl:EOF}

%build
# jcommon comes from the SCL-ized package. That's why we need to source
# the enable scriptlet.
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
CLASSPATH=$(build-classpath jcommon tomcat-servlet-api) \
    ant -f ant/build.xml compile javadoc

# Convert to OSGi bundle
java -Djfreechart.bundle.version="%{version}" -jar $(build-classpath aqute-bnd) \
   wrap -output lib/%{pkg_name}-%{version}.bar -properties %{SOURCE1} lib/%{pkg_name}-%{version}.jar
mv lib/%{pkg_name}-%{version}.bar %{pkg_name}-%{version}.jar
%mvn_artifact pom.xml %{pkg_name}-%{version}.jar
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install -J javadoc
%{?scl:EOF}

%files -f .mfiles
%doc ChangeLog licence-LGPL.txt NEWS README.txt

%files javadoc -f .mfiles-javadoc

%changelog
* Wed Jan 27 2016 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.14-60.6
- Rebuild for RHSCL 2.2.

* Tue Jan 20 2015 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.14-60.5
- Use java common's libs as BR.
- Use java common's requires/provides generators.

* Wed Dec 17 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.14-60.4
- Don't hard-code maven collection name.

* Wed Jun 18 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.14-60.3
- Remove Fedora conditionals.

* Tue Jun 17 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.14-60.2
- Add jcommon requires.

* Tue Jun 17 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.14-60.1
- Build against maven30 collection.

* Mon Jan 20 2014 Severin Gehwolf <sgehwolf@redhat.com> - 1.0.14-15
- Rebuild in order to fix osgi()-style provides.
- Resolves: RHBZ#1054813

* Wed Nov 27 2013 Omair Majid <omajid@redhat.com> 1.0.14-14
- Properly enable SCL.

* Mon Nov 18 2013 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-13
- Add macro for java auto-requires/provides.

* Mon Nov 11 2013 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-12
- Use build-classpath which now accounts for SCL-ized deps if
  properly enabled.

* Tue Sep 17 2013 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-11
- BR SCL-ized jcommon package.
- SCL-ize ant build command.

* Wed Aug 28 2013 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-10
- SCL-ize package.

* Tue Feb 19 2013 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-9
- Fix FTBFS due to build-classpath not finding swt.jar any
  longer. See RHBZ#912664.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.14-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Nov 21 2012 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-7
- Remove itext dependency in pom.

* Fri Nov 16 2012 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-6
- Conditionally build jfreechart-swt.

* Mon Sep 17 2012 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-4
- Set proper Bundle-{Version,SymbolicName,Name} in manifest.

* Tue Jul 24 2012 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-3
- Add aqute bnd instructions so as to produce OSGi metadata.
- Based on kdaniel's suggestion, use build-classpath script to find swt

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Apr 23 2012 Alexander Kurtakov <akurtako@redhat.com> 1.0.14-1
- Update to new upstream version 1.0.14.
- Use pom.xml file from the tarball.

* Wed Feb 15 2012 Marek Goldmann <mgoldman@redhat.com> 1.0.13-5
- Added Maven POM: BZ#789586

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.13-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Jun 29 2011 Alexander Kurtakov <akurtako@redhat.com> 1.0.13-3
- Adapt to current guidelines.

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Apr 19 2010 Lubomir Rintel <lkundrak@v3.sk> - 1.0.13-1
- Update to a later release
- Cosmetic fixes

* Mon Apr 19 2010 Lubomir Rintel <lkundrak@v3.sk> - 1.0.10-4
- Enable SWT support (ELMORABITY Mohamed, #583339)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jul 19 2008 Lubomir Rintel (Fedora Astronomy) <lkundrak@fedoraproject.org> - 1.0.10-1
- Initial packaging
