using PyCall
using Glob
psse34 = pyimport("psse34");
psspy = pyimport("psspy");
psspy.psseinit();
_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()
const dfx = pyimport("pssetools.dfx");
const acc = pyimport("pssetools.acc");
const acc_pp = pyimport("pssetools.acc_pp");
const acc_unzip = pyimport("pssetools.acc_unzip");
const cnv = pyimport("pssetools.cnv");
const dyn = pyimport("pssetools.dyn");
const snp = pyimport("pssetools.snp");
const dll = pyimport("pssetools.dll");


## INPUT FILES
cases = glob("src/*.sav")
sub_file = "src/estudio.sub"
mon_file = "src/estudio.mon"
con_file = "src/estudio.con"
idv_file = "src/estudio.idv"
dyr_file = ["src/gyr_25_v34_1.dyr"]
convload = ["src/convload.py"]
config   = "src/config.cfg"
dlls = glob("lib/*.dll")
log_dir = "log"
build_dir = "build"
results_dir = "results"
mkpath(log_dir)
mkpath(build_dir)
mkpath(results_dir)


## CLEAN 
files_to_remove = [
    "lib/usrdll.dll",
    glob(build_dir * "/*")...,
    glob(results_dir * "/*")...,
    glob(log_dir * "/*")...,
]
for path in files_to_remove
    run(`rm -rf $path`)    
end


## ESTATICO 
function estatico(case)
    case_basename = chopsuffix(basename(case), ".sav")
    args = (
        :sav => case,
        :sub => sub_file,
        :mon => mon_file,
        :con => con_file,
        :dfx => joinpath(build_dir, case_basename * ".dfx"),
        :zip => joinpath(build_dir, case_basename * ".zip"),
        :acc => joinpath(build_dir, case_basename * ".acc"),
        :frp => joinpath(build_dir, case_basename * ".frp"),
        :vrp => joinpath(build_dir, case_basename * ".vrp"),
        :folder => joinpath(results_dir, case_basename),
        :config => config,
    )
    ierr1 = dfx.run(; args...)
    ierr2 = acc.run(; args...)
    ierr3 = acc_unzip.run(; args...)
    ierr4 = acc_pp.run(; args...)
    return [ierr1, ierr2, ierr3, ierr4]
end
map(estatico, cases)


## CNV
function convertir(case)
    case_basename = chopsuffix(basename(case), ".sav")
    args = (
        :sav => case,
        :cnv => joinpath(build_dir, case_basename * ".cnv"),
        :py => convload,
    )
    ierr = cnv.run(;args...)
    return ierr
end
map(convertir, cases)


## SNP
snapshot = "snapshot.snp"
ierr = snp.run(
    sav=cases[1],
    snp=joinpath(build_dir, snapshot),
    dyr=dyr_file,
    cc=joinpath(build_dir, "cc.flx"),
    ct=joinpath(build_dir, "ct.flx"),
    idv=idv_file,
)


## COMPILA
run(`rm -f lib/usrdll.dll`)
run(`bash compila.sh`)


## DINAMICO
function dinamico(case, script)
    case_basename = chopsuffix(basename(case), ".cnv") 
    script_basename = chopsuffix(basename(script), ".py")
    ofile_basename = joinpath(
        results_dir, case_basename, 
        case_basename * "_" * script_basename
    )
    # incializar
    psspy.case(case)
    psspy.rstr(snapshot)
    for dll in dlls
        psspy.addmodellibrary(dll)
    end
    psspy.dynamics_solution_param_2(
        intgar1=250,
        realar1=0.15,
    )
    psspy.set_netfrq(1)
    psspy.strt_2(outfile=ofile_basename * ".outx")
    pyeval("execfile('$script')")
    psspy.save(ofile_basename * ".cnv")
end

dinamico("<caso>", "<script>")


