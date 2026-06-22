SUBROUTINE NOMBRE(MC, SLOT)
    INCLUDE 'COMON4.INS'
    USE OUTPUTMESSAGES_MODULE

    IMPLICIT NONE

    INTEGER MC, SLOT
    INTEGER J, K, L, M
    INTEGER IB
    INTEGER IDX ! DUMMY INDEX
    INTEGER NCONS, NSTATES, NVARS, NICONS

    REAL VT, VOUT, VINP

    EXTERNAL SHOW_MODEL_INDICIES
    INTRINSIC COS, SIN, ABS, ATAN2, CONJG

    NICONS  = 0          ! cantidad de 'ICON'
    NCONS   = 0          ! cantidad de 'CON'
    NSTATES = 0          ! cantidad de 'STATE'
    NVARS   = 0          ! cantidad de 'VAR'
    
    ! TODO checkear funcion para obtener indices STRTIN
    J = STRTIN(1, SLOT)  ! starting 'CON'
    K = STRTIN(2, SLOT)  ! starting 'STATE'
    L = STRTIN(3, SLOT)  ! starting 'VAR'
    M = STRTIN(4, SLOT)  ! starting 'ICON'


    SELECT CASE (MODE)
    CASE (1) ! INTIALIZATION .--------------------------------------------------
        IF (MIDTRM) RETURN



        RETURN

    CASE (2) ! DERIVATIVES -----------------------------------------------------
        IF (MIDTRM) RETURN



        RETURN

    CASE (3) ! OUTPUT ----------------------------------------------------------
        IF (MIDTRM) RETURN
        IF (KPAUSE.EQ.2) CALL KPAUSECHECK



        RETURN

    CASE (4) ! DYDA ------------------------------------------------------------
        CALL KPAUSECHECK
        IF (MIDTRM) THEN
            CALL NOTMID
            RETURN
        ENDIF
        NINTEG = MAX(NINTEG, K + NSTATES - 1)
        RETURN

    CASE (6) ! DYDA ------------------------------------------------------------
        IB = ABS(NUMTRM(MC))  ! bus sequence number

        ! TODO MODIFICAR SI ES NECESARIO EVITAR INFO
        WRITE (DBUF01, 507) NUMBUS(IB), MACHID(MC), &
               NICONS, NCONS, NSTATES, NVARS, &
               ICON(M:M+NICONS-1), &
               CON(J:J+NCONS-1)
        CALL REPORTS(IPRT, DBUF01, 3) ! TODO MODIFICAR N° DE LINEA
        RETURN

    CASE (5, 7) ! DOCUCHECK-----------------------------------------------------
        IF (MODE==5) CALL DOCUHEADING
        CALL SHOW_MODEL_INDICIES(M, M+NICONS-1,  &
                                 J, J+NCONS-1,   &
                                 K, K+NSTATES-1, &
                                 L, L+NVARS-1,   &
                                 0, 0)
        DO IDX=0, NCONS-1
            WRITE(DBUF01,7) IDX, CON(J+IDX)
            CALL REPORTS(IPRT, DBUF01, 1)
        END DO

        DO IDX=0, NICONS-1
            WRITE(DBUF01,17) IDX, ICON(M+IDX)
            CALL REPORTS(IPRT, DBUF01, 1)
        END DO
        
        RETURN

    CASE (8)
        ! TODO MODIFICAR
        J=1
        CON_DSCRPT(J+0)  = 'CON description'
        M=1
        ICON_DSCRPT(M+0) = 'ICON description'
        RETURN
    END SELECT

    ! T-ENTRY ------------------------------------------------------------------
    ENTRY NOMBRE(MC, SLOT)
    
    
    
    RETURN

  7  FORMAT (' CON(J+', I, ') = ', G13.5)
 17  FORMAT ('ICON(J+', I, ') = ', I)
507  FORMAT (I7,' ''USRMDL'' ', A2, ' ''NOMBRE'' IC IT', 4I2 &
             / ICONS(4X,I7) &
             / CONS(4X,G13.5), '/')

    CONTAINS
    SUBROUTINE KPAUSECHECK
        ! TODO CHECK SOMETHING AT KPAUSE IF IT IS NECCESARY
    END SUBROUTINE KPAUSECHECK
END SUBROUTINE NOMBRE

