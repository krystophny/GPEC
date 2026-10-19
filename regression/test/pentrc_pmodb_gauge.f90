! Run in the Solovev ideal example after dcon and gpec.
program pentrc_pmodb_gauge
    use params, only: r8
    use pentrc_interface, only: initialize_pentrc, nn
    use inputs, only: read_pmodb, dbob_m, divx_m, mfac, mpert
    use dcon_interface, only: jac_type
    use cspline_mod, only: cspline_eval
    implicit none
    character(512) :: filename
    character(32) :: chart
    integer :: run, u, i, j
    real(r8) :: psi
    complex(r8), allocatable :: first_b(:), first_d(:)
    call initialize_pentrc
    allocate(first_b(mpert), first_d(mpert))
    write(filename, '(a,i0,a)') 'test_pmodb_n', nn, '.out'
    do run=1,2
        open(newunit=u, file=trim(filename), status='replace')
        write(u,'(a)') 'psi m eul_re eul_im lag_re lag_im div_re div_im kap_re kap_im'
        do i=0,4
            psi=0.2_r8 + i*0.1_r8
            do j=1,mpert
                ! The same perpendicular pair, with deliberately different lagb gauges.
                write(u,'(10es24.15)') psi, real(mfac(j),r8), 0.0_r8, 0.0_r8, &
                    real(run*3,r8), real(run*2,r8), 0.2_r8, -0.1_r8, 0.7_r8, 0.3_r8
            end do
        end do
        close(u)
        chart=jac_type
        call read_pmodb(filename,chart,0,1,.false.)
        call cspline_eval(dbob_m,0.4_r8,0)
        call cspline_eval(divx_m,0.4_r8,0)
        if (run==1) then
            first_b=dbob_m%f
            first_d=divx_m%f
        else
            if (maxval(abs(dbob_m%f-first_b)) > 1.0e-12_r8) &
                error stop 'pmodb drive depends on unrelated lagb gauge'
            if (maxval(abs(divx_m%f-first_d)) > 1.0e-12_r8) &
                error stop 'pmodb Jacobian depends on unrelated lagb gauge'
        end if
    end do
    if (maxval(abs(first_b)) == 0) error stop 'empty drive'
    print '(a)', 'PASS: pmodb perpendicular pair is independent of lagb gauge'
end program pentrc_pmodb_gauge
