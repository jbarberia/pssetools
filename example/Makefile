
# archivos de configuracion
# ------------------------------------------------------------------------------
sav = $(wildcard *.sav)
sub = test.sub
mon = test.mon
con = test.con

dyn = flat1.py
src = lib/mod3424_1.lib
dll = $(wildcard lib/*.dll)
dyr = gyr_24_v34_1.dyr
cnv_script = convload_sadi.py

runner1 = test_runner.py

# config = foo

RESULTS = results
BUILD = build
# Note: adjusted output extension if needed, keeping .outx for now as in original
OUTX = $(foreach s, $(sav), $(addprefix $(basename ${s})-,$(dyn:.py=.outx)))

# shortcuts
# ------------------------------------------------------------------------------
# PSSETOOLS CLI
CLI = pssetools

.PHONY: estatico reporte_flujos reporte_tensiones
.PHONY: dinamico snapshot compilacion simulacion 
.PRECIOUS: $(BUILD)/%.dfx $(BUILD)/%.acc

estatico: reporte_flujos reporte_tensiones
	awk 'FNR==1 && NR!=1 {next} {print}' $(BUILD)/*.frp > $(RESULTS)/flow.csv
	awk 'FNR==1 && NR!=1 {next} {print}' $(BUILD)/*.vrp > $(RESULTS)/volt.csv
reporte_flujos:    $(patsubst %.sav, $(BUILD)/%.frp, $(sav))
reporte_tensiones: $(patsubst %.sav, $(BUILD)/%.vrp, $(sav))

dinamico:    conversion compilacion simulacion
conversion:  $(patsubst %.sav, $(BUILD)/%.cnv, $(sav))
compilacion: $(BUILD)/usrdll.dll
simulacion:  $(addprefix $(RESULTS)/,$(OUTX))

runner: $(patsubst %.sav, $(BUILD)/runner1_%.txt, $(sav))

# ESTATICO ---------------------------------------------------------------------
$(BUILD)/%.frp $(BUILD)/%.vrp: $(BUILD)/%.acc | $(BUILD)
	@echo -----------
	@echo armando frp
	@echo $^
	@echo $@
	$(CLI) acc-pp 
		--acc $(BUILD)/$*.acc 
		--frp $(BUILD)/$*.frp 
		--vrp $(BUILD)/$*.vrp
	
$(BUILD)/%.acc: %.sav $(BUILD)/%.dfx | $(BUILD) $(RESULTS)
	@echo -----------
	@echo armando acc	
	@echo $^
	@echo $*
	$(CLI) acc 
		--sav $*.sav 
		--acc $(BUILD)/$*.acc 
		--dfx $(BUILD)/$*.dfx 
		--zipfile $(RESULTS)/$*.zip
	
$(RESULTS)/%.acc.zip: $(BUILD)/%.acc
	@true

$(BUILD)/%.dfx: %.sav $(sub) $(mon) $(con) | $(BUILD) 
	@echo -----------
	@echo armando dfx
	@echo $^
	$(CLI) dfx 
		--sav $*.sav 
		--sub $(sub) 
		--mon $(mon) 
		--con $(con) 
		--dfx $@

# DINAMICO ---------------------------------------------------------------------
$(RESULTS)/%.outx: $(BUILD)/usrdll.dll $(dll) | $(RESULTS) 
	$(CLI) dyn 
		--out $@ 
		--snp $(BUILD)/snapshot.snp 
		--dll $(BUILD)/usrdll.dll $(dll) 
		--no-debug
		
$(BUILD)/%.cnv: %.sav | $(BUILD)
	@echo
	@echo armando cnv
	@echo ------------
	@echo $^
	$(CLI) cnv 
		--cnv $@ 
		--sav $^ 
		--py $(cnv_script)

$(BUILD)/snapshot.snp: $(sav)| $(BUILD)
	@echo
	@echo snapshot
	@echo --------
	$(CLI) snp 
		--snp $(BUILD)/snapshot.snp 
		--dyr $(dyr) 
		--cc  $(BUILD)/conec.flx 
		--ct  $(BUILD)/conet.flx 
		--sav $<

$(BUILD)/conec.flx $(BUILD)/conet.flx: $(BUILD)/snapshot.snp
	@true

$(BUILD)/usrdll.dll: $(BUILD)/snapshot.snp $(BUILD)/conec.flx $(BUILD)/conet.flx
	@echo
	@echo compilacion
	@echo ------------
	$(CLI) dll 
		--dll $@ 
		--sources $(BUILD)/conec.flx $(BUILD)/conet.flx $(src)

# RUNNER -----------------------------------------------------------------------
$(BUILD)/runner1_%.txt: %.sav | $(BUILD)
	$(CLI) runner 
		--sav $^ 
		--report $@ 
		--script $(runner1)

# ------------------------------------------------------------------------------
$(BUILD):
	@mkdir -p $(BUILD)

$(RESULTS):
	@mkdir -p $(RESULTS)
