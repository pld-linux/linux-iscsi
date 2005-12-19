#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	iSCSI - SCSI over IP
Summary(pl):	iSCSI - SCSI po IP
Name:		linux-iscsi
Version:	4.0.2
%define		_rel 0.1
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/linux-iscsi/%{name}-%{version}.tgz
# Source0-md5:	da77c95464a57abe2cdd8d00323bb477
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-sysfs.patch
URL:		http://linux-iscsi.sourceforge.net/
%{?with_dist_kernel:BuildRequires:	kernel-headers >= 2.6.0}
BuildRequires:	sysfsutils-static
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin

%description
The Linux iSCSI driver acts as an iSCSI protocol initiator to
transport SCSI requests and responses over an IP network between the
client and an iSCSI-enabled target device such as a Cisco SN 5420
storage router. The iSCSI protocol is an IETF-defined protocol for IP
storage. For more information about the iSCSI protocol, refer to the
IETF standards for IP storage at <http://www.ietf.org/>.

%description -l pl
Sterownik Linux iSCSI zachowuje siê jak inicjator protoko³u iSCSI do
transportu zleceñ SCSI i odpowiedzi po sieci IP miêdzy klientem a
urz±dzeniem docelowym obs³uguj±cym iSCSI, takim jak Cisco SN 5420.
Protokó³ iSCSI jest zdefiniowany przez IETF do sk³adowania IP. Wiêcej
informacji o protokole iSCSI znajduje siê w standardach IETF na
<http://www.ietf.org/>.

%package -n kernel-iscsi
Summary:	ISCSI kernel module
Summary(pl):	Modu³ j±dra ISCSI
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	%{name} = %{version}-%{release}

%description -n kernel-iscsi
IP over SCSI kernel module.

%description -n kernel-iscsi -l pl
Modu³ j±dra dla protoko³u IP over SCSI.

%package -n kernel-smp-iscsi
Summary:	ISCSI SMP kernel module
Summary(pl):	Modu³ j±dra SMP ISCSI
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	%{name} = %{version}-%{release}

%description -n kernel-smp-iscsi
IP over SCSI SMP kernel module.

%description -n kernel-smp-iscsi -l pl
Modu³ j±dra SMP dla protoko³u IP over SCSI.

%prep
%setup -q
%patch0 -p1

%build
%if %{with kernel}
sed -i -e "s#\$(pwd)#$(pwd)#g" -e "s#driver/include#driver/include-iscsi#g" driver/Makefile
cd driver
mv include include-iscsi
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER

	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	mv iscsi_sfnet{,-$cfg}.ko
done
cd ..
%endif

%if %{with userspace}
%{__make} user \
	CC="%{__cc}"
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_mandir}/man{1,5,8},/etc/{rc.d/init.d,sysconfig}}
install -d $RPM_BUILD_ROOT/var/lib/iscsi

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
install iscsi_sfnet-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/iscsi_sfnet.ko
%if %{with smp} && %{with dist_kernel}
install iscsi_sfnet-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/iscsi_sfnet.ko
%endif
%endif

%if %{with userspace}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/iscsi
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/iscsi

install misc/iscsi.conf $RPM_BUILD_ROOT%{_sysconfdir}
:> $RPM_BUILD_ROOT%{_sysconfdir}/fstab.iscsi
:> $RPM_BUILD_ROOT%{_sysconfdir}/initiatorname.iscsi

:> $RPM_BUILD_ROOT/var/lib/iscsi/bindings

install misc/scripts/iscsi-mountall misc/scripts/iscsi-umountall misc/scripts/iscsi-ls $RPM_BUILD_ROOT%{_sbindir}

install man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1
install man/*.5 $RPM_BUILD_ROOT%{_mandir}/man5
install man/*.8 $RPM_BUILD_ROOT%{_mandir}/man8

cd Linux-*/obj
install utils/iscsi-boot/init $RPM_BUILD_ROOT%{_sbindir}/iscsi-init
install utils/iscsi-device utils/iscsi-iname iscsid $RPM_BUILD_ROOT%{_sbindir}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-iscsi
%depmod %{_kernel_ver}

%postun -n kernel-iscsi
%depmod %{_kernel_ver}

%post -n kernel-smp-iscsi
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-iscsi
%depmod %{_kernel_ver}smp

%post
/sbin/chkconfig --add iscsi
#if [ -f /var/lock/subsys/iscsi ]; then
#	/etc/rc.d/init.d/iscsi restart 1>&2
#else
#	echo "Type \"/etc/rc.d/init.d/iscsi start\" to start iscsi" 1>&2
#fi

if ! grep -q "^InitiatorName=[^ \t\n]" /etc/initiatorname.iscsi 2>/dev/null ; then
	echo "InitiatorName=$(iscsi-iname)" >> /etc/initiatorname.iscsi
fi

%preun
if [ "$1" = "0" ]; then
#	if [ -f /var/lock/subsys/iscsi ]; then
#		/etc/rc.d/init.d/iscsi stop >&2
#	fi
	/sbin/chkconfig --del iscsi
fi

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_sbindir}/*
%attr(750,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/iscsi.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fstab.iscsi
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/initiatorname.iscsi
%dir /var/lib/iscsi
%ghost /var/lib/iscsi/bindings
%{_mandir}/man?/*
%attr(754,root,root) /etc/rc.d/init.d/iscsi
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/iscsi
%endif

%if %{with kernel}
%files -n kernel-iscsi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-iscsi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*
%endif
%endif
