%define fedora		1
%define redhat		0
%if %{fedora}
%define gcj_support	1
%else
%define gcj_support	0
%endif

%define eclipse_name	eclipse
%define eclipse_base	%{_datadir}/%{eclipse_name}

Name:		eclipse-phpeclipse
Version:	1.1.8
Release:	%mkrel 16.4.2
Summary:	PHP Eclipse plugin

Group:		Development/Java
License:	CPL
URL:		http://phpeclipse.net/

Source0:	phpeclipse-%{version}.tar.gz
Source1:	make-phpeclipse-source-archive.sh

Patch0:		%{name}-3.2-build.patch
Patch1:		%{name}-rm-win32-help.patch
Patch2:		%{name}-httpd-integration.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires:  eclipse-pde
BuildRequires:  java-rpmbuild
%if %{gcj_support}
BuildRequires:		gcc-java >= 0:4.0.2
BuildRequires:		java-gcj-compat-devel >= 0:1.0.33
%else
BuildRequires:		java-devel >= 0:1.4.2
%endif

%if %{gcj_support}
ExclusiveArch:		%{ix86} x86_64 ppc ia64
%else
BuildArch:		noarch
%endif

Requires:		eclipse-platform >= 1:3.2.1
Requires:		eclipse-pde-runtime
Requires: 		php
Requires:		apache

%description
The PHPeclipse plugin allows developers to write PHP webpages and scripts in
Eclipse. 

%prep
%setup -q -n phpeclipse-1.1.8

pushd net.sourceforge.phpeclipse
%patch0 -p0
popd 
pushd net.sourceforge.phpeclipse.phphelp
%patch1 -p0
popd
%patch2

%{__sed} --in-place "s:/usr/share/eclipse:%{eclipse_base}:" net.sourceforge.phpeclipse.externaltools/prefs/default_linux.properties
%{__sed} --in-place 's/\r//' net.sourceforge.phpeclipse.feature/cpl-v10.html

%build
# See comments in the script to understand this.
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK %{eclipse_base}
SDK=$(cd SDK > /dev/null && pwd)

# Eclipse may try to write to the home directory.
mkdir home
homedir=$(cd home > /dev/null && pwd)

# build the main phpeclipse feature
#	TODO: convert this to an `eclipse` command
%{java} -cp $SDK/startup.jar \
	-Dosgi.sharedConfiguration.area=%{_libdir}/eclipse/configuration \
	-Duser.home=$homedir \
	org.eclipse.core.launcher.Main \
	-application org.eclipse.ant.core.antRunner \
	-DjavacFailOnError=true \
	-DdontUnzip=true \
	-Dtype=feature \
	-Did=net.sourceforge.phpeclipse \
	-DsourceDirectory=$(pwd) \
	-DbaseLocation=$SDK \
	-Dbuilder=%{eclipse_base}/plugins/org.eclipse.pde.build/templates/package-build \
	-DdontFetchAnything=true \
	-f %{eclipse_base}/plugins/org.eclipse.pde.build/scripts/build.xml

%install
rm -rf $RPM_BUILD_ROOT
install -d -m 755 $RPM_BUILD_ROOT%{eclipse_base}
unzip -q -d $RPM_BUILD_ROOT%{eclipse_base}/.. build/rpmBuild/net.sourceforge.phpeclipse.zip
rm $RPM_BUILD_ROOT%{eclipse_base}/plugins/org.eclipse.pde.runtime*.jar

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root,-)
%doc %{eclipse_base}/features/net.sourceforge.phpeclipse_%{version}/cpl-v10.html
%{eclipse_base}/features/net.sourceforge.phpeclipse_*
%{eclipse_base}/plugins/net.sourceforge.phpdt.smarty.ui_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.core_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.debug.core_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.debug.ui_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.externaltools_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.launching_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.phphelp_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.ui_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.webbrowser_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.xml.core_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.xml.ui_*
%if %{gcj_support}
%{_libdir}/gcj/%{name}
%endif


