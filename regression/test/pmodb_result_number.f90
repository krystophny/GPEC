program pmodb_number
    use params, only: r8
    use pentrc_interface, only: initialize_pentrc, nn, zi, mi, wdfac, electron
    use inputs, only: read_pmodb, dbob_m, divx_m, mfac
    use dcon_interface, only: jac_type
    use cspline_mod, only: cspline_eval
    use torque, only: tpsi
    implicit none
    character(32) :: chart
    character(512) :: filename
    complex(r8) :: actual
    integer :: k
    call initialize_pentrc
    chart=jac_type
    filename='gpec_pmodb_n1.out'
    call read_pmodb(filename,chart,0,1,.false.)
    call cspline_eval(dbob_m,0.4_r8,0)
    call cspline_eval(divx_m,0.4_r8,0)
    k=minloc(abs(mfac),dim=1)
    print '(a,i0,4es24.15)', 'PMODB psi=0.4 m=',mfac(k),dbob_m%f(k),divx_m%f(k)
    call tpsi(actual,0.4_r8,nn,0,zi,mi,wdfac,1.0_r8,electron,'fcgl')
    print '(a,2es24.15)', 'PMODB Im(Tpsi_fcgl) at psi=0.4: ',aimag(actual)
end program pmodb_number
