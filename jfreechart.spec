%{?scl:%scl_package jfreechart}
%{!?scl:%global pkg_name %{name}}

# Use java common's requires/provides generator
%{?java_common_find_provides_and_requires}

# Exclude generation of osgi() style provides, since they are not
# SCL-namespaced and may conflict with base RHEL packages.
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1045437
%global __provides_exclude ^osgi(.*)$

Name:           %{?scl_prefix}jfreechart
Version:        1.0.14
# Release should be higher than el6 builds. Use convention
# 60.X where X is an increasing int. 60 for rhel-6. We use
# 70.X for rhel-7. For some reason we cannot rely on the
# dist tag.
Release:        70.4%{?dist}
Summary:        Java chart library

Group:          Development/Libraries
License:        LGPLv2+
URL:            http://www.jfree.org/jfreechart/
Source0:        http://download.sourceforge.net/sourceforge/jfreechart/%{pkg_name}-%{version}.tar.gz
Source1:        bnd.properties

Requires:       java
Requires:       servlet
Requires:       %{?scl_prefix}jcommon >= 1.0.17
BuildRequires:  %{?scl_prefix_java_common}ant
BuildRequires:  %{?scl_prefix_java_common}mvn(javax.servlet:servlet-api)
BuildRequires:  %{?scl_prefix}jcommon >= 1.0.17
BuildRequires:  %{?scl_prefix_java_common}javapackages-local
%if 0%{?fedora}
BuildRequires:  eclipse-swt
%endif
# Required for converting jars to OSGi bundles
BuildRequires:  %{?scl_prefix_maven}aqute-bnd

%{?scl:Requires: %scl_runtime}

BuildArch:      noarch
Patch0:         remove_itext_dep.patch

%description
JFreeChart is a free 100% Java chart library that makes it easy for
developers to display professional quality charts in their applications.

%if 0%{?fedora}
%package swt
Summary:        Experimental swt extension for jfreechart
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       eclipse-swt jpackage-utils

%description swt
Experimental swt extension for jfreechart.
%endif

%package javadoc
Summary:        Javadocs for %{name}
Group:          Documentation
%{?scl:Requires: %scl_runtime}

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

%if 0%{?fedora}
# See RHBZ#912664. There seems to be some dispute about build-classpath.
# So don't use it for swt.
ant -f ant/build-swt.xml \
        -Dswt.jar=%{_libdir}/eclipse/swt.jar \
        -Djcommon.jar=$(build-classpath jcommon) \
        -Djfreechart.jar=lib/jfreechart-%{version}.jar
%endif
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

%if 0%{?fedora}
%files swt
%{_javadir}/%{name}/swtgraphics2d*.jar
%{_javadir}/%{name}/%{name}-swt*.jar
%endif

%files javadoc -f .mfiles-javadoc

%changelog
* Mon Jan 19 2015 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-70.4
- Use java common's libs as BR.

* Mon Jan 12 2015 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-70.3
- Make package buildable with latest xmvn (2.2.x).

* Fri Dec 19 2014 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-70.2
- Use maven30 collection for building.
- Use java common's requires/provides generators.

* Mon Jun 23 2014 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-70.1
- Fix dependency on scl-runtime.
- Bump release number to allow for in-place upgrade.

* Fri Dec 20 2013 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-14
- Don't generate osgi() style provides.
- Resolves: RHBZ#1045437.

* Wed Nov 27 2013 Severin Gehwolf <sgehwolf@redhat.com> 1.0.14-13
- Properly enalbe SCL.

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
