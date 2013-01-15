%define bootstrap 0
%define _emacs_sitelispdir %{_datadir}/emacs/site-lisp
%define _emacs_bytecompile %{_bindir}/emacs -batch --no-init-file --no-site-file --eval '(progn (setq load-path (cons "." load-path)))' -f batch-byte-compile
%define _xemacs_sitelispdir %{_datadir}/xemacs/site-lisp
%define _xemacs_bytecompile %{_bindir}/xemacs -q -no-site-file -batch -eval '(push "." load-path)' -f batch-byte-compile

%global upstreamver 4r5p7
%global pkgdate 2012_12_14-17_45
%global gapdirname gap%(echo %upstreamver | cut -dp -f1)
%global gapdir %{_prefix}/lib/gap
%global icondir %{_datadir}/icons/hicolor

Name:           gap
Version:        %(echo %upstreamver | sed -r "s/r|p/./g")
Release:        3%{?dist}
Summary:        Computational discrete algebra

Group:          Sciences/Mathematics
License:        GPLv2+
URL:            http://www.gap-system.org/
Source0:        ftp://ftp.gap-system.org/pub/gap/gap4/tar.bz2/%{name}%{upstreamver}_%{pkgdate}.tar.bz2
Source1:        gap-README.fedora
Source2:        update-gap-workspace
Source3:        gap.xml
Source4:        gap.desktop
Source5:        gap.el
Source6:        gap.1.in
Source7:        gac.1.in
Source8:        update-gap-workspace.1
Source9:        gap.vim
# rpm5 does not understand heredoc with double %%
Source10:       gap.macros
# This patch from Debian rearranges some paths to match Linux conventions.
Patch0:         %{name}-paths.patch
# This patch applies a change from Debian to allow help files to be in gzip
# compressed DVI files, and also adds support for viewing with xdg-open.
Patch1:         %{name}-help.patch
# This patch will not be sent upstream.  It makes the main binary read the
# environment variables now read by gap.sh, so we can dispose of the shell
# script and run the actual binary directly.
Patch2:         %{name}-env.patch
# This patch was sent upstream 4 Aug 2011.  It fixes some cosmetic issues in
# the Emacs Lisp sources.
Patch3:         %{name}-emacs.patch

BuildRequires:  desktop-file-utils
BuildRequires:  gmp-devel
BuildRequires:  netpbm
BuildRequires:  readline-devel
BuildRequires:  emacs
BuildRequires:  xemacs
Obsoletes:      gap-system <= 4.4.12
Obsoletes:      gap-system-packages <= 4.4.12

Requires:       %{name}-libs = %{version}-%{release}
Requires:       %{name}-core%{?_isa} = %{version}-%{release}
Requires:       %{name}-online-help = %{version}-%{release}
Requires:       meataxe

%description
GAP is a system for computational discrete algebra, with particular
emphasis on Computational Group Theory.  GAP provides a programming
language, a library of thousands of functions implementing algebraic
algorithms written in the GAP language as well as large data libraries
of algebraic objects.  GAP is used in research and teaching for studying
groups and their representations, rings, vector spaces, algebras,
combinatorial structures, and more.

This is a metapackage that requires the standard GAP components.

%package libs
Summary:        Essential GAP libraries
Group:          Sciences/Mathematics
BuildArch:      noarch

Provides:       %{name}-prim-groups = %{version}-%{release}
Provides:       %{name}-small-groups = %{version}-%{release}
Provides:       %{name}-trans-groups = %{version}-%{release}

%description libs
This package contains the essential GAP libraries: lib and grp, as well as
the primitive, small, and transitive group databases.

%package core
Summary:        GAP core components
Group:          Sciences/Mathematics
Requires:       %{name}-libs = %{version}-%{release}
%if !%{bootstrap}
Requires:       GAPDoc
%endif
# The gap binary executes gunzip
Requires:       gzip
Requires:       hicolor-icon-theme

%description core
This package contains the core GAP system.

%package online-help
Summary:        Online help for GAP
Group:          Sciences/Mathematics
Requires:       %{name}-core = %{version}-%{release}
BuildArch:      noarch

%description online-help
This package contains the documentation in TeX format needed for GAP's
online help system.

%package devel
Summary:        GAP compiler and development files
Group:          Development/Other
Requires:       %{name}-core%{?isa} = %{version}-%{release}
Requires:       gcc
Requires:       gmp-devel%{?_isa}

%description devel
This package contains the GAP compiler (gac) and the header files necessary
for developing GAP programs.

%package vim
Summary:        Edit GAP files with VIM
Group:          Sciences/Mathematics
Requires:       %{name}-core = %{version}-%{release}, vim-enhanced
BuildArch:      noarch

%description vim
This package provides VIM add-on files to support editing GAP sources.
Both syntax highlighting and indentation are supported.

%package emacs
Summary:        Edit GAP files with Emacs
Group:          Sciences/Mathematics
Requires:       %{name}-core = %{version}-%{release}
Requires:       emacs
BuildArch:      noarch

%description emacs
This package provides Emacs add-on files to support editing GAP sources
and running GAP from within Emacs.

%package emacs-el
Summary:        Emacs Lisp source files for GAP
Group:          Sciences/Mathematics
Requires:       %{name}-emacs = %{version}-%{release}
BuildArch:      noarch

%description emacs-el
Emacs Lisp source files for GAP.  This package is not needed to use the
GAP Emacs support.

%package xemacs
Summary:        Edit GAP files with XEmacs
Group:          Sciences/Mathematics
Requires:       %{name}-core = %{version}-%{release}
Requires:       xemacs
BuildArch:      noarch

%description xemacs
This package provides XEmacs add-on files to support editing GAP sources
and running GAP from within XEmacs.

%package xemacs-el
Summary:        XEmacs Lisp source files for GAP
Group:          Sciences/Mathematics
Requires:       %{name}-xemacs = %{version}-%{release}
BuildArch:      noarch

%description xemacs-el
XEmacs Lisp source files for GAP.  This package is not needed to use the
GAP XEmacs support.

%prep
%setup -q -n %{gapdirname}
%patch0
%patch1
%patch2
%patch3

# Replace the CFLAGS, find the math functions and sigsetjmp
sed -re "s|(gp_cv_prog_cc_cdynoptions=)\"-fpic -Wall -O2|\1\"\$RPM_OPT_FLAGS -fPIC -D_GNU_SOURCE -DSYS_DEFAULT_PATHS='\"%{gapdir}\"'|" \
    -e "s|(gp_cv_prog_cc_cdynlinking=)\"-shared -g|\1\"\$RPM_OPT_FLAGS -shared|" \
    -e '/log2 log10/iLIBS="-lm $LIBS"' \
    -e "/sigsetjmp/,\$s|(ac_fn_c_check_func.*)ac_func(.*)|\1{ac_func/sigsetjmp/__sigsetjmp}\2|" \
    -i cnf/configure.out

# The -m32 and -m64 flags are not available on all platforms, and we provide
# them in optflags when they are needed.
sed -e 's/GMP_CFLAGS="-m${ABI}"/GMP_CFLAGS=""/' \
    -e 's/ABI_CFLAGS="-m[[:digit:]]*"/ABI_CFLAGS=""/' \
    -i configure

# Get the README
cp -p %{SOURCE1} README.fedora

# Fix a missing executable bit
chmod a+x makepkgs

%build
%configure --with-gmp=system \
  CFLAGS='%{optflags} -D_GNU_SOURCE -DSYS_DEFAULT_PATHS=\"%{gapdir}\"'
# FIXME: GAP 4.5 broke %%{?_smp_mflags}
make

# Get the value of the GAParch variable
source ./sysinfo.gap

# The packages must be built for the check script to succeed
sed -e "s|@gaparch@|$GAParch|" \
    -e "s| -DSYS_DEFAULT_PATHS=\\\"/usr/share/gap\\\"||" \
    -i bin/$GAParch/gac
mkdir -p bin/$GAParch/extern/gmp/include
ln -s %{_includedir}/gmp.h bin/$GAParch/extern/gmp/include
sed -i "s|-D_GNU_SOURCE|-I$PWD|" Makefile-default*
sed -i "s|-o|-p -I -p $PWD -p -I -p $PWD/bin/$GAParch &|" \
    pkg/edim/Makefile.in pkg/Browse/Makefile.in
make packages

# Compress help files
find doc -name \*.dvi -o -name \*.toc | xargs gzip --best

# Compress large group files
find -O3 small -mindepth 2 -type f | xargs gzip --best -f
gzip --best prim/grps/*.g trans/*.grp

%install
# Get the value of the GAParch variable
source ./sysinfo.gap

# Install the binaries
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cp -p bin/$GAParch/{gac,gap} $RPM_BUILD_ROOT%{_bindir}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}

# Install the data
mkdir -p $RPM_BUILD_ROOT%{gapdir}/etc
cp -a grp lib prim small trans tst $RPM_BUILD_ROOT%{gapdir}
cp -p etc/debug* $RPM_BUILD_ROOT%{gapdir}/etc

# Install the arch-specific files
cp -a sysinfo.gap* $RPM_BUILD_ROOT%{gapdir}

# Create the system workspace, initially empty
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}
touch $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/workspace

# Install the header and object files where the GAP compiler can find them
mkdir -p $RPM_BUILD_ROOT%{gapdir}/src
cp -p src/*.h $RPM_BUILD_ROOT%{gapdir}/src
mkdir -p $RPM_BUILD_ROOT%{gapdir}/bin/$GAParch
cp -p bin/$GAParch/config.h $RPM_BUILD_ROOT%{gapdir}/bin/$GAParch
cp -p bin/$GAParch/*.o $RPM_BUILD_ROOT%{gapdir}/bin/$GAParch
rm -f bin/$GAParch/extern/Makefile
cp -a bin/$GAParch/extern $RPM_BUILD_ROOT%{gapdir}/bin/$GAParch
ln -s %{_bindir}/gac $RPM_BUILD_ROOT%{gapdir}/bin/$GAParch/gac
ln -s %{_bindir}/gap $RPM_BUILD_ROOT%{gapdir}/bin/$GAParch/gap

# Make an empty directory to hold the GAP packages
mkdir -p $RPM_BUILD_ROOT%{gapdir}/pkg

# Intall the documentation
cp -a doc $RPM_BUILD_ROOT%{gapdir}
rm -f $RPM_BUILD_ROOT%{gapdir}/doc/manualindex
rm -fr $RPM_BUILD_ROOT%{gapdir}/doc/test

# Install the icon
mkdir -p $RPM_BUILD_ROOT%{icondir}/32x32
bmptopnm bin/gapicon.bmp | pnmtopng -compression=9 \
         > $RPM_BUILD_ROOT%{icondir}/32x32/gap.png

# Install the MIME type
mkdir -p $RPM_BUILD_ROOT%{_datadir}/mime/packages
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/mime/packages

# Install the desktop file
mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
desktop-file-install --mode=644 --dir=$RPM_BUILD_ROOT%{_datadir}/applications \
  %{SOURCE4}

# Install the RPM macro file
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm/macros.d
cp -p %{SOURCE10} $RPM_BUILD_ROOT%{_sysconfdir}/rpm/macros.d

# Install the VIM support
mkdir -p $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/indent
cp -p etc/gap_indent.vim $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/indent
mkdir -p $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/syntax
cp -p etc/gap.vim $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/syntax
mkdir -p $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/ftdetect
cp -p %{SOURCE9}  $RPM_BUILD_ROOT%{_datadir}/vim/vimfiles/ftdetect

# Install the Emacs support
mkdir -p $RPM_BUILD_ROOT%{_emacs_sitelispdir}
cp -p etc/emacs/gap*.el $RPM_BUILD_ROOT%{_emacs_sitelispdir}
pushd $RPM_BUILD_ROOT%{_emacs_sitelispdir}
%{_emacs_bytecompile} gap*.el
popd
mkdir -p $RPM_BUILD_ROOT%{_emacs_sitestartdir}
cp -p %{SOURCE5} $RPM_BUILD_ROOT%{_emacs_sitestartdir}

# Install the XEmacs support
mkdir -p $RPM_BUILD_ROOT%{_xemacs_sitelispdir}
cp -p etc/emacs/gap*.el $RPM_BUILD_ROOT%{_xemacs_sitelispdir}
pushd $RPM_BUILD_ROOT%{_xemacs_sitelispdir}
%{_xemacs_bytecompile} gap*.el
popd
mkdir -p $RPM_BUILD_ROOT%{_xemacs_sitestartdir}
cp -p %{SOURCE5} $RPM_BUILD_ROOT%{_xemacs_sitestartdir}

# Install the man pages
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
sed "s|@VERSION@|%{version}|" %{SOURCE6} > $RPM_BUILD_ROOT%{_mandir}/man1/gap.1
sed "s|@VERSION@|%{version}|" %{SOURCE7} > $RPM_BUILD_ROOT%{_mandir}/man1/gac.1
cp -p %{SOURCE8} $RPM_BUILD_ROOT%{_mandir}/man1

%post core
update-desktop-database %{_datadir}/applications &>/dev/null ||:
update-mime-database %{_datadir}/mime &>/dev/null ||:
touch --no-create %{icondir} >&/dev/null ||:
%{_bindir}/update-gap-workspace ||:

%posttrans
%{_bindir}/gtk-update-icon-cache %{icondir} >&/dev/null ||:

%postun core
update-desktop-database %{_datadir}/applications &>/dev/null ||:
update-mime-database %{_datadir}/mime &>/dev/null ||:
if [ $1 -eq 0 ] ; then
touch --no-create %{icondir} >&/dev/null ||:
%{_bindir}/gtk-update-icon-cache %{icondir} >&/dev/null ||:
fi

%check
sed -e "s|^GAP_DIR=.*|GAP_DIR=$PWD|" \
    -e "s|\$GAP_DIR/bin/\$GAP_PRG|$PWD/bin/\$GAP_PRG|" \
    -i bin/gap.sh bin/gap-default*.sh
sed -i "s|80 -r|& -l $PWD|" Makefile-default*
make testinstall

%files
# No files in the metapackage

%files libs
%doc etc/GPL small/README
%dir %{gapdir}
%{gapdir}/grp/
%{gapdir}/lib/
%{gapdir}/prim/
%{gapdir}/small/
%{gapdir}/trans/

%files core
%doc README.fedora
%{_bindir}/gap
%{_bindir}/update-gap-workspace
%{gapdir}/sysinfo.gap*
%{gapdir}/pkg/
%{_mandir}/man1/gap.1*
%{_mandir}/man1/update-gap-workspace.1*
%{_datadir}/applications/gap.desktop
%{_datadir}/mime/packages/gap.xml
%{icondir}/32x32/gap.png
%dir %{_localstatedir}/lib/%{name}/
%verify(user group mode) %{_localstatedir}/lib/%{name}/workspace

%files online-help
%{gapdir}/doc/

%files devel
%{_bindir}/gac
%{gapdir}/bin/
%{gapdir}/src/
%{gapdir}/tst/
%{_mandir}/man1/gac.1*
%config(noreplace) %{_sysconfdir}/rpm/macros.d/gap.macros

%files vim
%{gapdir}/etc/
%{_datadir}/vim/vimfiles/ftdetect/gap.vim
%{_datadir}/vim/vimfiles/indent/gap_indent.vim
%{_datadir}/vim/vimfiles/syntax/gap.vim

%files emacs
%doc etc/emacs/gap-mode.doc
%{_emacs_sitelispdir}/gap*.elc
%{_emacs_sitestartdir}/gap.el

%files emacs-el
%{_emacs_sitelispdir}/gap*.el

%files xemacs
%doc etc/emacs/gap-mode.doc
%{_xemacs_sitelispdir}/gap*.elc
%{_xemacs_sitestartdir}/gap.el

%files xemacs-el
%{_xemacs_sitelispdir}/gap*.el

%changelog
* Tue Jan 15 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 4.5.7-3
- Correct version in macros.gap

* Tue Jan 15 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 4.5.7-2
- Rebuild after bootstrap

* Tue Jan 15 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 4.5.7-1
- Import and bootstrap in openmandriva

* Fri Dec 21 2012 Rex Dieter <rdieter@fedoraproject.org> 4.5.7-2
- optimize/update icon scriptlets

* Mon Dec 17 2012 Jerry James <loganjerry@gmail.com> - 4.5.7-1
- New upstream release

* Mon Oct 22 2012 Jerry James <loganjerry@gmail.com> - 4.5.6-3
- Further fixes for the -m32/-m64 issue
- Many packages need the primitive, small, or transitive groups; collapse them
  all into the -libs subpackage so they are always available
- Provide sysinfo-default[32|64], as required by some packages
- Provide symbolic links to gac and gap from the bin directory, as required by
  some packages

* Sat Oct 20 2012 Peter Robinson <pbrobinson@fedoraproject.org>	4.5.6-2
- -m32/-m64 should come from RPM_OPT_FLAGS. Fix build issues on non x86 arches

* Mon Sep 24 2012 Jerry James <loganjerry@gmail.com> - 4.5.6-1
- New upstream release
- Remove unused patches from git

* Thu Sep 13 2012 Jerry James <loganjerry@gmail.com> - 4.5.5-1
- New upstream release
- Drop upstreamed patches
- Sources are now UTF-8; no conversion necessary

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.4.12-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jan 31 2012 Jerry James <loganjerry@gmail.com> - 4.4.12-4
- Add an RPM macro file for GAP packages
- Fix the location of config.h

* Wed Jan 11 2012 Jerry James <loganjerry@gmail.com> - 4.4.12-3
- Fix problems found on review

* Tue Jan  3 2012 Jerry James <loganjerry@gmail.com> - 4.4.12-2
- Mimic Debian's subpackage structure

* Wed Oct 12 2011 Jerry James <loganjerry@gmail.com> - 4.4.12-1
- Initial RPM
