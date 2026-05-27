# ==============================
# SE PUEDE MODIFICAR (config)
# ==============================
CONFIG := src/config.cfg

SAVS := $(wildcard src/*.sav)
SUB := src/estudio.sub
MON := src/estudio.mon
CON := src/estudio.con

SNP_SAV ?= $(firstword $(SAVS))
IDV := src/estudio.idv
CNV_PY := src/convload.py
DYR_FILES := $(wildcard src/*.dyr)

# Dinamico (producto SAV x PY)
DYN_PY := $(wildcard src/D*.py)
DYN_DLLS ?= $(DLL_OUT) $(wildcard src/*.dll)
DYN_NO_DEBUG :=


# ==============================
# SE PUEDE MODIFICAR (dll)
# ==============================
DLL_OUT := src/dsurs.dll
DLL_EXTRA_SOURCES := src/mod3424_1.lib
DLL_SOURCES = $(wildcard $(BUILD_DIR)/*.flx) $(wildcard src/*.f90) $(DLL_EXTRA_SOURCES)


# ==============================
# SE PUEDE MODIFICAR (rutas)
# ==============================
BUILD_DIR := build
RESULTS_DIR := results
LOG_DIR := log


# ==============================
# NO TOCAR (variables derivadas)
# ==============================
DFX       := $(SAVS:src/%.sav=$(BUILD_DIR)/%.dfx)
ACC       := $(SAVS:src/%.sav=$(BUILD_DIR)/%.acc)
ASCC      := $(SAVS:src/%.sav=$(RESULTS_DIR)/%.scf)
CNV       := $(SAVS:src/%.sav=$(BUILD_DIR)/%.cnv)
ACC_ZIP   := $(SAVS:src/%.sav=$(RESULTS_DIR)/%.zip)
ACC_UNZIP_DIRS := $(SAVS:src/%.sav=$(RESULTS_DIR)/%_acc_unzip)
FRP            := $(SAVS:src/%.sav=$(RESULTS_DIR)/%.frp)
VRP            := $(SAVS:src/%.sav=$(RESULTS_DIR)/%.vrp)
SNP_BASE       := $(basename $(notdir $(SNP_SAV)))
SNP            := $(BUILD_DIR)/$(SNP_BASE).snp
CC             := $(BUILD_DIR)/$(SNP_BASE)_cc.flx
CT             := $(BUILD_DIR)/$(SNP_BASE)_ct.flx
SAV_BASES      := $(basename $(notdir $(SAVS)))
DYN_PY_BASES   := $(basename $(notdir $(DYN_PY)))
DYN_OUTS := $(foreach s,$(SAV_BASES),$(foreach p,$(DYN_PY_BASES),$(RESULTS_DIR)/dyn_$(s)_$(p)/$(s)_$(p).out))


# ==============================
# NO TOCAR (reglas)
# ==============================
$(BUILD_DIR) $(RESULTS_DIR) $(LOG_DIR):
	mkdir -p $@

$(RESULTS_DIR)/dyn_%: | $(RESULTS_DIR)
	mkdir -p $@

$(BUILD_DIR)/%.dfx: src/%.sav $(SUB) $(MON) $(CON) | $(BUILD_DIR) $(LOG_DIR)
	python -m pssetools dfx $< $(SUB) $(MON) $(CON) --dfx $@ > $(LOG_DIR)/$*.dfx.log 2>&1
	
$(BUILD_DIR)/%.acc $(RESULTS_DIR)/%.zip: src/%.sav $(BUILD_DIR)/%.dfx $(CONFIG) | $(BUILD_DIR) $(RESULTS_DIR) $(LOG_DIR)
	python -m pssetools acc $< --acc $(BUILD_DIR)/$*.acc --dfx $(BUILD_DIR)/$*.dfx --zipfile $(RESULTS_DIR)/$*.zip --config $(CONFIG) > $(LOG_DIR)/$*.acc.log 2>&1

$(BUILD_DIR)/%.cnv: src/%.sav $(CONFIG) $(CNV_PY) | $(BUILD_DIR) $(LOG_DIR)
	python -m pssetools cnv $< --cnv $@ --config $(CONFIG) $(if $(CNV_PY),--py $(CNV_PY),) > $(LOG_DIR)/$*.cnv.log 2>&1

$(SNP): $(SNP_SAV) $(IDV) $(DYR_FILES) | $(BUILD_DIR) $(LOG_DIR)
	python -m pssetools snp $(SNP_SAV) --snp $(SNP) --cc $(CC) --ct $(CT) --idv $(IDV) $(if $(DYR_FILES),--dyr $(DYR_FILES),) --config $(CONFIG) > $(LOG_DIR)/$(SNP_BASE).snp.log 2>&1

$(DLL_OUT): $(DLL_SOURCES) $(CONFIG) | $(BUILD_DIR) $(LOG_DIR)
	C:/Python314/python.exe -m pssetools dll --dll $@ --sources $(DLL_SOURCES) --config $(CONFIG) > $(LOG_DIR)/dll.log 2>&1

define DYN_RULE
$(RESULTS_DIR)/dyn_$(1)_$(2)/$(1)_$(2).out: $(BUILD_DIR)/$(1).cnv $(SNP) $(filter %/$(2).py $(2).py,$(DYN_PY)) $(DYN_DLLS) | $(RESULTS_DIR)/dyn_$(1)_$(2) $(LOG_DIR)
	python -m pssetools dyn --cnv $(BUILD_DIR)/$(1).cnv --snp $(SNP) --out $$@ $(if $(DYN_DLLS),--dll $(DYN_DLLS),) --py $(filter %/$(2).py $(2).py,$(DYN_PY)) $(if $(DYN_NO_DEBUG),--no-debug,) > $(LOG_DIR)/$(1)_$(2).dyn.log 2>&1
endef
$(foreach s,$(SAV_BASES),$(foreach p,$(DYN_PY_BASES),$(eval $(call DYN_RULE,$(s),$(p)))))

$(RESULTS_DIR)/%.frp $(RESULTS_DIR)/%.vrp: $(BUILD_DIR)/%.acc $(CONFIG) | $(RESULTS_DIR) $(LOG_DIR)
	python -m pssetools acc-pp --acc $< --frp $(RESULTS_DIR)/$*.frp --vrp $(RESULTS_DIR)/$*.vrp --config $(CONFIG) > $(LOG_DIR)/$*.acc-pp.log 2>&1

$(RESULTS_DIR)/%_acc_unzip: $(RESULTS_DIR)/%.zip | $(RESULTS_DIR) $(LOG_DIR)
	python -m pssetools acc-unzip --zipfile $< --folder $@ > $(LOG_DIR)/$*.acc-unzip.log 2>&1

$(RESULTS_DIR)/%.scf: src/%.sav $(SUB) $(CONFIG) | $(RESULTS_DIR) $(LOG_DIR)
	python -m pssetools ascc $< $(SUB) --report $@ --config $(CONFIG) > $(LOG_DIR)/$*.ascc.log 2>&1


# ==============================
# SE PUEDE MODIFICAR (targets)
# ==============================
.PHONY: estatico dinamico cortocircuito cnv snapshot dll dyn clean

cortocircuito: $(ASCC)

dinamico: dyn
dyn: dll
dll: snapshot
snapshot: cnv

cnv: $(CNV)
snapshot: $(SNP)
dll: $(DLL_OUT)
dyn: $(DYN_OUTS)

estatico: $(DFX) $(ACC) $(FRP) $(VRP) $(ACC_ZIP) $(ACC_UNZIP_DIRS)

clean:
	rm -rf $(BUILD_DIR)/*
	rm -rf $(RESULTS_DIR)/*
	rm -rf $(LOG_DIR)/*
	rm -f $(DLL_OUT)
