Summary:	iSCSI - SCSI over IP
Summary(pl):	iSCSI - SCSI po IP
Name:		linux-iscsi
Version:	4.0.1.1
%define		_rel 2
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/%{name}/%{name}-%{version}.tgz
# Source0-md5:	52a251da7c8b56c08dde61fa0400eba2
Patch0:		%{name}-Makefile.patch
URL:		http://linux-iscsi.sourceforge.net/
BuildRequires:	kernel-source
BuildRequires:	kernel-module-build
BuildRequires:	glibc-static
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The Linux iSCSI driver acts as an iSCSI protocol initiator to
transport SCSI requests and responses over an IP network between the
client and an iSCSI-enabled target device such as a Cisco SN 5420
storage router. The iSCSI protocol is an IETF-defined protocol for IP
storage. For more information about the iSCSI protocol, refer to the
IETF standards for IP storage at http://www.ietf.org/ .

%description -l pl
Sterownik Linux iSCSI zachouje siê jak inicjator protoko³u iSCSI do
transportu zleceñ SCSI i odpowiedzi po sieci IP miêdzy klientem a
urz±dzeniem docelowym obs³uguj±cym iSCSI, takim jak Cisco SN 5420.
Protokó³ iSCSI jest zdefiniowany przez IETF do sk³adowania IP. Wiêcej
informacji o protokole iSCSI znaajduje siê w standardach IETF na
http://www.ietf.org/ .

%package -n kernel-iscsi
Summary:	ISCSI kernel module
Summary(pl):	Modu³ j±dra ISCSI
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	%{name} = %{version}

%description -n kernel-iscsi
IP over SCSI kernel module.

%description -n kernel-iscsi -l pl
Modu³ j±dra dla protoko³u IP over SCSI.

%package -n kernel-smp-iscsi
Summary:	ISCSI SMP kernel module
Summary(pl):	Modu³ j±dra SMP ISCSI
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	%{name} = %{version}

%description -n kernel-smp-iscsi
IP over SCSI SMP kernel module.

%description -n kernel-smp-iscsi -l pl
Modu³ j±dra SMP dla protoko³u IP over SCSI.

%prep
%setup -q
%patch0 -p1

%build
rm -rf build-done include
install -d build-done/{UP,SMP}
ln -sf %{_kernelsrcdir}/config-up .config
install -d include/{linux,config}
ln -sf %{_kernelsrcdir}/include/linux/autoconf-up.h include/linux/autoconf.h
ln -sf %{_kernelsrcdir}/include/asm-%{_arch} include/linux/asm
touch include/config/MARKER

%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 modules

mv iscsi.ko build-done/UP/
%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 mrproper

ln -sf %{_kernelsrcdir}/config-smp .config
ln -sf %{_kernelsrcdir}/include/linux/autoconf-smp.h include/linux/autoconf.h
touch include/config/MARKER

%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 modules

mv iscsi.ko build-done/SMP/

# build daemon
%{__make} OBJDIR=./build-done daemons
%{__make} OBJDIR=./build-done tools
%{__make} OBJDIR=./build-done utils


%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_mandir}/{man1,man5,man8},/etc/rc.d/init.d}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc

install build-done/SMP/* $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
install build-done/UP/* $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc

install build-done/{iscsid,iscsigt,iscsi-device,iscsi-iname,iscsi-ls} $RPM_BUILD_ROOT%{_sbindir}
install {iscsi-*mountall,mkinitrd.iscsi} $RPM_BUILD_ROOT%{_sbindir}
install iscsi.conf $RPM_BUILD_ROOT/etc
install iscsi-ls.1 $RPM_BUILD_ROOT%{_mandir}/man1/iscsi-ls.1
install iscsid.8 $RPM_BUILD_ROOT%{_mandir}/man8/iscsid.8
install iscsi.conf.5 $RPM_BUILD_ROOT%{_mandir}/man5/iscsi.conf.5

install rc.iscsi $RPM_BUILD_ROOT/etc/rc.d/init.d/iscsi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}*
%attr(755,root,root) /etc/rc.d/init.d/iscsi
%attr(644,root,root) /etc/iscsi.conf
%attr(644,root,root) %{_mandir}/man8/*
%attr(644,root,root) %{_mandir}/man5/*
%attr(644,root,root) %{_mandir}/man1/*

%files -n kernel-iscsi
%defattr(644,root,root,755)
%attr(644,root,root) /lib/modules/%{_kernel_ver}/misc/*

%files -n kernel-smp-iscsi
%defattr(644,root,root,755)
%attr(644,root,root) /lib/modules/%{_kernel_ver}smp/misc/*
