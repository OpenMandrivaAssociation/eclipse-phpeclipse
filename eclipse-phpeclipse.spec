%define eclipse_base     %{_libdir}/eclipse
%define gcj_support      0

Name:		eclipse-phpeclipse
Version:	1.2.0
Release:	%mkrel 0.2.svn1573.1
Summary:	PHP Eclipse plugin

Group:		Development/PHP
License:	CPL
URL:		http://phpeclipse.net/

# source tarball and the script used to generate it from upstream's source control
# script usage:
# $ sh get-phpeclipse.sh
Source0:   phpeclipse-%{version}.tar.gz
Source1:   get-phpeclipse.sh

Patch0:    %{name}-broken-help-links.patch
Patch1:    %{name}-fix-build-props.patch
Patch2:    %{name}-httpd-integration.patch
Patch3:    %{name}-no-htmlparser.patch
Patch4:    %{name}-rm-win32-help.patch
Patch5:    %{name}-external-parser.patch
Patch6:    %{name}-external-preview.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires:  eclipse-pde
BuildRequires:  java-rpmbuild
BuildRequires:  zip
BuildRequires:  tomcat5-jsp-2.0-api
%if %{gcj_support}
BuildRequires:		gcc-java >= 0:4.0.2
BuildRequires:		java-gcj-compat-devel >= 0:1.0.33
%else
BuildRequires:		java-devel >= 0:1.4.2
%endif

%if %{gcj_support}
ExclusiveArch:		%{ix86} x86_64 ppc ia64
%else
#BuildArch:		noarch
%endif

Requires:		eclipse-platform >= 1:3.2.1
Requires:		eclipse-pde-runtime
Requires: 		php
Requires:		apache

%description
PHPEclipse is an open source PHP IDE based on the Eclipse platform. Features
supported include syntax highlighting, content assist, PHP manual integration,
templates and support for the XDebug and DBG debuggers.

%prep
%setup -q -n phpeclipse-%{version}

# apply patches
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0
%patch5 -p0
%patch6 -p0

# ditch bundled libs in favor of building against fedora packaged libs
rm net.sourceforge.phpeclipse.phpmanual.htmlparser/sax2.jar \
   net.sourceforge.phpeclipse.phpmanual.htmlparser/htmllexer.jar \
   net.sourceforge.phpeclipse.phpmanual.htmlparser/filterbuilder.jar \
   net.sourceforge.phpeclipse.phpmanual.htmlparser/thumbelina.jar \
   net.sourceforge.phpeclipse.phpmanual.htmlparser/junit.jar \
   net.sourceforge.phpeclipse.phpmanual.htmlparser/htmlparser.jar
build-jar-repository -s -p net.sourceforge.phpeclipse.phpmanual.htmlparser xml-commons-apis

# this is done in a patch instead
#grep -lR sax2 * | xargs sed --in-place "s/sax2/xml-commons-apis/"

# fix jar versions
find -name MANIFEST.MF | xargs sed --in-place "s/0.0.0/%{version}/"

# make sure upstream hasn't sneaked in any jars we don't know about
JARS=""
for j in `find -name "*.jar"`; do
  if [ ! -L $j ]; then
    JARS="$JARS $j"
  fi
done
if [ ! -z "$JARS" ]; then
   echo "These jars should be deleted and symlinked to system jars: $JARS"
   exit 1
fi

%build
# build the main feature
%{eclipse_base}/buildscripts/pdebuild -D -f net.sourceforge.phpeclipse.feature

# build the debug features
%{eclipse_base}/buildscripts/pdebuild -D -f net.sourceforge.phpeclipse.debug.feature
%{eclipse_base}/buildscripts/pdebuild -D -f net.sourceforge.phpeclipse.xdebug.feature

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{eclipse_base}
unzip -q -d %{buildroot}%{eclipse_base}/.. build/rpmBuild/net.sourceforge.phpeclipse.feature.zip
unzip -q -d %{buildroot}%{eclipse_base}/.. build/rpmBuild/net.sourceforge.phpeclipse.debug.feature.zip
unzip -q -d %{buildroot}%{eclipse_base}/.. build/rpmBuild/net.sourceforge.phpeclipse.xdebug.feature.zip

# need to recreate the symlinks to libraries that were setup in "prep"
# because for some reason the ant copy task doesn't preserve them
pushd %{buildroot}%{eclipse_base}/plugins/net.sourceforge.phpeclipse.phpmanual.htmlparser_*
rm *.jar
build-jar-repository -s -p . xml-commons-apis
popd

%{gcj_compile}

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
%doc %{eclipse_base}/features/net.sourceforge.phpeclipse.feature_*/cpl-v10.html

# main feature
%{eclipse_base}/features/net.sourceforge.phpeclipse.feature_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.core_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.externaltools_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.help_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.phphelp_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.phpmanual_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.phpmanual.htmlparser_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.smarty.ui_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.ui_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.webbrowser_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.xml.core_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.xml.ui_*

# debug features
%{eclipse_base}/features/net.sourceforge.phpeclipse.debug.feature_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.debug.core_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.debug.ui_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.launching_*
%{eclipse_base}/features/net.sourceforge.phpeclipse.xdebug.feature_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.xdebug.core_*
%{eclipse_base}/plugins/net.sourceforge.phpeclipse.xdebug.ui_*
%{gcj_files}


