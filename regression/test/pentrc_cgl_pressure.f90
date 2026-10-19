! Run in the Solovev ideal example after dcon and gpec.
program pentrc_cgl_pressure
    use params, only: r8, xj
    use pentrc_interface, only: initialize_pentrc, nn, zi, mi, wdfac, electron
    use torque, only: tpsi
    use inputs, only: dbob_m, divx_m, mfac, mthsurf, rzphi, kin
    use spline_mod, only: spline_type, spline_alloc, spline_fit, spline_int, spline_eval
    use bicube_mod, only: bicube_eval
    implicit none
    type(spline_type) :: volume
    integer :: i, k
    real(r8) :: psi, work, expected_im
    complex(r8) :: d, kap, b, pp, pa, actual
    call initialize_pentrc
    psi = 0.4_r8
    d = cmplx(1.0_r8, 2.0_r8, r8)
    kap = cmplx(0.7_r8, -0.3_r8, r8)
    b = -(d + kap)
    pp = -d + b
    pa = -3*d - 2*b
    work = -real((pa-pp)*conjg(b) + pa*conjg(d), r8)/2
    k = minloc(abs(mfac), dim=1)
    if (mfac(k) /= 0) error stop 'test requires m=0 in the example spectrum'
    dbob_m%fs = 0
    divx_m%fs = 0
    dbob_m%fs(:, k) = b
    divx_m%fs(:, k) = d
    ! Refit the interpolants used by the actual torque path.
    block
        use cspline_mod, only: cspline_fit
        call cspline_fit(dbob_m, 'extrap')
        call cspline_fit(divx_m, 'extrap')
    end block
    call tpsi(actual, psi, nn, 0, zi, mi, wdfac, 1.0_r8, electron, 'fcgl')
    call spline_alloc(volume, mthsurf, 1)
    do i = 0, mthsurf
        volume%xs(i) = real(i, r8)/mthsurf
        call bicube_eval(rzphi, psi, volume%xs(i), 0)
        volume%fs(i, 1) = rzphi%f(4)
    end do
    call spline_fit(volume, 'periodic')
    call spline_int(volume)
    call spline_eval(kin, psi, 0)
    ! Half of pressure work is the real-Fourier-mode quadratic normalization.
    expected_im = nn*kin%f(1)*kin%f(3)*work*volume%fsi(mthsurf, 1)
    print '(a,2es22.12)', 'CGL actual/pressure work: ', aimag(actual), expected_im
    if (abs(actual-xj*expected_im) > 1.0e-10_r8*abs(expected_im)) &
        error stop 'CGL torque differs from double-adiabatic pressure work'
end program pentrc_cgl_pressure
