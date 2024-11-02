
SimAppProUFCCuedOptionBase = "UFC_OptionCueing"
SimAppProDelimeter = '-----------------------------------------'
SimAppProNewLine = '\n'
SimAppProNullValue = '\n'

class UFCSimAppProHelper:

    def __init__(self, ufc_payload ):
        self.ufc_payload = ufc_payload
    
    def get_ufc_payload_string(self):
        return self.build_sim_app_pro_ufc_payload(self.ufc_payload)

    def build_sim_app_pro_ufc_command(self, key, value):
        return f"{SimAppProDelimeter}{SimAppProNewLine}{key}{SimAppProNewLine}{value}{SimAppProNewLine}"

    def clean_text(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, int):
            return str(value)
        else:
            return SimAppProNullValue


    def build_sim_app_pro_cued_window_payload(self, selected_windows_table):
        cued_windows = {}
        string_payload_for_sim_app_pro = ""

        selected_windows = selected_windows_table if selected_windows_table is not None else []

        # Populate 5 empty window options
        for i in range(1, 6):
            cued_windows[f"SimAppProUFCCuedOptionBase{i}"] = ""

        for window_position in selected_windows:
            key_cued_window = f"SimAppProUFCCuedOptionBase{window_position}"
            cued_windows[key_cued_window] = ":"

        # Loop over windows and generate compatible SimApp Pro transmission
        for key, value in cued_windows.items():
            string_payload_for_sim_app_pro += self.build_sim_app_pro_ufc_command(key, value)

        # Usable string payload for SimApp Pro
        return string_payload_for_sim_app_pro

    # SimApp treats 10-20 special. "`0" == 10
    def build_sim_app_pro_com_payload(self, com_string):
        com_number = int(com_string) if com_string.isdigit() else None
        com_result_string = com_string
        if isinstance(com_number, int):
            if 10 <= com_number < 20:
                com_result_string = "`" + str(com_number % 10)
        return com_result_string


    # SimApp Pro Payload = {
    #     option1 = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String length 4. Letters and digits
    #     option2 = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String length 4. Letters and digits
    #     option3 = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String length 4. Letters and digits
    #     option4 = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String length 4. Letters and digits
    #     option5 = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String length 4. Letters and digits
    #     scratchPadNumbers = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String length 4. Digits only
    #     scratchPadString1 = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String length 1. Single character only A-Z or 0-9
    #     scratchPadString2 = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String Length 1. Single character only A-Z or 0-9
    #     com1 = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String length 1. Single character A-Z or integer 0-99 (some oddities above 10)
    #     com2 = ufcPatch.ufcPatchUtils.SimAppProNullValue, -- String length 1. Single character A-Z or integer 0-99 (some oddities above 10)
    #     selectedWindows = {} -- Array of strings representing which selected window positions have a :
    # }
    def build_sim_app_pro_ufc_payload(self, sim_app_pro_ufc_data_map):
        option1 = self.build_sim_app_pro_ufc_command("UFC_OptionDisplay1", self.clean_text(sim_app_pro_ufc_data_map['option1']))
        option2 = self.build_sim_app_pro_ufc_command("UFC_OptionDisplay2", self.clean_text(sim_app_pro_ufc_data_map['option2']))
        option3 = self.build_sim_app_pro_ufc_command("UFC_OptionDisplay3", self.clean_text(sim_app_pro_ufc_data_map['option3']))
        option4 = self.build_sim_app_pro_ufc_command("UFC_OptionDisplay4", self.clean_text(sim_app_pro_ufc_data_map['option4']))
        option5 = self.build_sim_app_pro_ufc_command("UFC_OptionDisplay5", self.clean_text(sim_app_pro_ufc_data_map['option5']))
        scratch_digits = self.build_sim_app_pro_ufc_command("UFC_ScratchPadNumberDisplay",
                                                    self.clean_text(sim_app_pro_ufc_data_map['scratchPadNumbers']))
        scratch_left_string = self.build_sim_app_pro_ufc_command("UFC_ScratchPadString1Display",
                                                            self.clean_text(sim_app_pro_ufc_data_map['scratchPadString1']))
        scratch_right_string = self.build_sim_app_pro_ufc_command("UFC_ScratchPadString2Display",
                                                            self.clean_text(sim_app_pro_ufc_data_map['scratchPadString2']))
        cued_windows_payload = self.build_sim_app_pro_cued_window_payload(sim_app_pro_ufc_data_map['selectedWindows'])
        com1_string_value = self.build_sim_app_pro_com_payload(sim_app_pro_ufc_data_map['com1'])
        com2_string_value = self.build_sim_app_pro_com_payload(sim_app_pro_ufc_data_map['com2'])
        com1 = self.build_sim_app_pro_ufc_command("UFC_Comm1Display", self.clean_text(com1_string_value))
        com2 = self.build_sim_app_pro_ufc_command("UFC_Comm2Display", self.clean_text(com2_string_value))
        return option1 + option2 + option3 + option4 + option5 + com1 + com2 + scratch_digits + scratch_left_string + scratch_right_string + cued_windows_payload
