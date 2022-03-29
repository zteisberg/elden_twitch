from contextlib import suppress

import pymem

from better_pattern import pattern_find_allocated


class EldenRingMod:
    
    def get_hud_base_address(self):
        return int.from_bytes(pymem.memory.read_bytes(self.pm.process_handle, int.from_bytes(
            pymem.memory.read_bytes(self.pm.process_handle, self.hud_address_pointer, 8), "little"), 8), "little")

    def get_hp_address(self):
        return self.get_hud_base_address() + 0x138

    def get_hp(self):
        return pymem.memory.read_int(self.pm.process_handle, self.get_hp_address())

    def set_hp(self, amount):
        pymem.memory.write_int(self.pm.process_handle, self.get_hp_address(), amount)

    def get_maxhp_address(self):
        return self.get_hud_base_address() + 0x13C

    def get_maxhp(self):
        return pymem.memory.read_int(self.pm.process_handle, self.get_maxhp_address())

    def set_maxhp(self, amount):
        pymem.memory.write_int(self.pm.process_handle, self.get_maxhp_address(), amount)

    def get_fp_address(self):
        return self.get_hud_base_address() + 0x144

    def get_fp(self):
        return pymem.memory.read_int(self.pm.process_handle, self.get_fp_address())

    def set_fp(self, amount):
        pymem.memory.write_int(self.pm.process_handle, self.get_fp_address(), amount)

    def get_stamina_address(self):
        return self.get_hud_base_address() + 0x158

    def get_stamina(self):
        return pymem.memory.read_int(self.pm.process_handle, self.get_stamina_address())

    def set_stamina(self, amount):
        pymem.memory.write_int(self.pm.process_handle, self.get_stamina_address(), amount)

    def kill_player(self):
        self.set_hp(0)

    def get_stats_base_address(self):
        first_level = int.from_bytes(pymem.memory.read_bytes(self.pm.process_handle, self.stats_base_address_pointer, 8),
                                     "little")
        second_level = int.from_bytes(pymem.memory.read_bytes(self.pm.process_handle, first_level + 0x08, 8), "little")
        return second_level

    def get_level_address(self):
        return self.get_stats_base_address() + 0x68

    def get_level(self):
        return pymem.memory.read_int(self.pm.process_handle, self.get_level_address())

    def set_level(self, amount):
        pymem.memory.write_int(self.pm.process_handle, self.get_level_address(), amount)

    def get_runes_address(self):
        return self.get_stats_base_address() + 0x6C

    def get_runes(self):
        return pymem.memory.read_int(self.pm.process_handle, self.get_runes_address())

    def set_runes(self, amount):
        pymem.memory.write_int(self.pm.process_handle, self.get_runes_address(), amount)

    def get_head_size_address(self):
        return self.get_stats_base_address() + 0x870

    def get_head_size(self):
        return pymem.memory.read_float(self.pm.process_handle, self.get_head_size_address())

    def set_head_size(self, amount):
        pymem.memory.write_float(self.pm.process_handle, self.get_head_size_address(), amount)

    def get_left_arm_size_address(self):
        return self.get_stats_base_address() + 0x87C

    def get_left_arm_size(self):
        return pymem.memory.read_float(self.pm.process_handle, self.get_left_arm_size_address())

    def set_left_arm_size(self, amount):
        pymem.memory.write_float(self.pm.process_handle, self.get_left_arm_size_address(), amount)

    def get_endurance_address(self):
        return self.get_stats_base_address() + 0x44

    def get_endurance(self):
        return pymem.memory.read_int(self.pm.process_handle, self.get_endurance_address())

    def set_endurance(self, amount):
        pymem.memory.write_int(self.pm.process_handle, self.get_endurance_address(), amount)
    
    def __init__(self):
        self.pm = pymem.Pymem('eldenring.exe')
        module_elden_ring = pymem.process.module_from_name(self.pm.process_handle, "eldenring.exe")

        hud_address_signature = b"\x45\xa5\x66\x38\xf9\x98\xf8\x79\xc1\x82\x76\xd6\xe1\xda\x97\x45\xf7\xd2\x6e\x64\xa9\x4d\xe3\x81\x27\x3c\x53\xa5\xb7\xa0\x5c\x99"
        stats_address_signature = b"\xc2\xc8\xb5\xce\x32\x1b\xba\xed\x0f\x14\x8b\x0c\xeb\x99\xff\x23\xc9\x6a\xe8\x7e\x0b\x55\xfc\xd2\x9b\x14\x53\xe1\x35\x6b\x2e\x27"

        self.hud_address_pointer = None
        self.stats_base_address_pointer = None
        
        with suppress(Exception):
            self.hud_address_pointer = pattern_find_allocated(self.pm.process_handle, b".\xa5..\xf9\x98\xf8.\xc1\x82.\xd6\xe1\xda\x97.\xf7\xd2..\xa9.\xe3\x81...\xa5\xb7\xa0.\x99") - 8
            # Since it uses regex behind the scenes, it's better to just wildcard characters that happen to be ascii
            self.stats_base_address_pointer = pattern_find_allocated(self.pm.process_handle, b"\xc2\xc8\xb5\xce.\x1b\xba\xed\x0f\x14\x8b\x0c\xeb\x99\xff.\xc9.\xe8.\x0b.\xfc\xd2\x9b\x14.\xe1....") - 8
            print("Elden Ring Connection Ready")
        
        if not (self.hud_address_pointer or self.stats_base_address_pointer):
            # Find location of opcodes that accesses HP/FP/Stamina (don't need to search for entire code segment, just enough to be unique)
            # mov ecx,[rax+????] 8B 88 ????
            # mov [rsi+????],ecx 89 8E ????
            # mov rax,[r14+....] - 49 8b 86
            aob_pattern = b"\x8b\x88....\x89\x8e....\x49\x8b\x86"
            opcode_address = pymem.pattern.pattern_scan_module(self.pm.process_handle, module_elden_ring, aob_pattern, return_multiple=False)
            # Copy the opcodes that we'll have to replace. It needs to be at least 14 bytes to fit a far jump, and we can't cut
            # an opcode in half so we have to take a full 19 bytes (should look similar to the AOB since this is
            # what we searched for, in this case it's just slightly longer.
            # mov ecx,[rax+????] 8B 88 ? ? ? ?
            # mov [rsi+????],ecx 89 8E ? ? ? ?
            # mov rax,[r14+????] - 49 8b 86 ? ? ? ?
            original_opcode = pymem.memory.read_bytes(self.pm.process_handle, opcode_address, 19)
        
            # Allocate memory to store an address for the HP/FP/Stamina
            # (and an extra 24 bytes for a signature to quickly reconnect to an already hacked eldenring instance)
            self.hud_address_pointer = self.pm.allocate(40)
            pymem.memory.write_bytes(self.pm.process_handle, self.hud_address_pointer+8, hud_address_signature, 32)
            # Allocate memory to store new instructions
            code_cave_address = self.pm.allocate(1000)
        
            # Build a script that stores rax (the register that has the address we need when the opcode above executes)
            # into our known memory space (hud_address_pointer)
            # since we will need to overwrite the opcode to divert to these instructions, we'll also need to add the instructions
            # we are overwriting to keep the game working.
            code_cave_script = bytearray(b'')
            # Add original opcodes that we are overwriting (19 bytes) - See lines 137-139 for what this looks like
            code_cave_script.extend(original_opcode)
            # Save hud_base_address during intercepted code into hud_address_pointer - mov [hud_address_pointer], rax
            code_cave_script.extend(b'\x48\xA3')
            code_cave_script.extend(self.hud_address_pointer.to_bytes(8, byteorder="little"))
            # Jump back to instructions after overwritten code - jmp ???????? (opcode_address + 19)
            code_cave_script.extend(b'\xFF\x25\x00\x00\x00\x00')
            code_cave_script.extend((opcode_address + 19).to_bytes(8, byteorder="little"))
            # Write the script to the code cave
            pymem.memory.write_bytes(self.pm.process_handle, code_cave_address, bytes(code_cave_script), 43)
        
            # Build a script that jumps to the code cave, overwriting the old accessing opcodes (Should total 19 bytes)
            overwrite_script = bytearray(b'')
            # Jump to code_cave - jmp ???????? (code_cave_address)
            overwrite_script.extend(b'\xFF\x25\x00\x00\x00\x00')
            overwrite_script.extend(code_cave_address.to_bytes(8, byteorder="little"))
            # We need to overwrite the empty space, best to put nops here in case we accidentally jump too early
            # but anything can go here safely in theory
            # nop - 90
            # nop - 90
            # nop - 90
            # nop - 90
            # nop - 90
            overwrite_script.extend(b'\x90\x90\x90\x90\x90')
            # Write the detour code over the original opcodes
            # Next time this code is invoked in the game, now the code in the code cave will activate every time, updating
            # hud_address_pointer with the pointer address we need to read/modify hp/fp/stamina
            pymem.memory.write_bytes(self.pm.process_handle, opcode_address, bytes(overwrite_script), 19)
        
        
            # Find location of opcodes that accesses most other stats (don't need to search for entire code segment, just enough to be unique)
            # mov rdx,[rcx+?] - 48 8B 51 ?
            # test rdx,rdx - 48 85 D2
            # je ???? - 0F84 ????
            # cmp byte ptr [rdx+....],. - 80 BA
            stats_aob_pattern = b"\x48\x8b\x51.\x48\x85\xd2\x0f\x84....\x80\xba"
            stats_opcode_address = pymem.pattern.pattern_scan_module(self.pm.process_handle, module_elden_ring, stats_aob_pattern, return_multiple=False)
            # Copy the opcodes that we'll have to replace. It needs to be at least 14 bytes to fit a far jump, and we can't cut
            # an opcode in half so we have to take a full 20 bytes (should look similar to the AOB since this is
            # what we searched for, in this case it's just slightly longer.
            # mov rdx,[rcx+?] - 48 8B 51 ?
            # test rdx,rdx - 48 85 D2
            # je ???? - 0F84 ????
            # cmp byte ptr [rdx+????],? - 80 BA ???? ?
            stats_original_opcode = pymem.memory.read_bytes(self.pm.process_handle, stats_opcode_address, 20)
        
            self.stats_base_address_pointer = self.pm.allocate(40)
            pymem.memory.write_bytes(self.pm.process_handle, self.stats_base_address_pointer+8, stats_address_signature, 32)
            stats_code_cave_address = self.pm.allocate(1000)
        
            stats_code_cave_script = bytearray(b'')
            # Save stat address during intercept (15 bytes)
            # push rax
            # mov rax,rcx
            # mov [stats_base_address_pointer], rax
            # pop rax
            stats_code_cave_script.extend(b'\x50\x48\x89\xC8\x48\xA3')
            stats_code_cave_script.extend(self.stats_base_address_pointer.to_bytes(8, byteorder="little"))
            stats_code_cave_script.extend(b'\x58')
            # Add original bytecode that we are overwriting (20 bytes) Probably need to modify jmps
            stats_code_cave_script.extend(stats_original_opcode[0:7])
            # je +19
            stats_code_cave_script.extend(b'\x74\x15')
            stats_code_cave_script.extend(stats_original_opcode[13:])
            # Jump to instructions after overwritten code
            stats_code_cave_script.extend(b'\xFF\x25\x00\x00\x00\x00')
            stats_code_cave_script.extend((stats_opcode_address + 20).to_bytes(8, byteorder="little"))
            stats_code_cave_script.extend(b'\xFF\x25\x00\x00\x00\x00')
            stats_code_cave_script.extend((stats_opcode_address + 0x108).to_bytes(8, byteorder="little"))
            pymem.memory.write_bytes(self.pm.process_handle, stats_code_cave_address, bytes(stats_code_cave_script), len(stats_code_cave_script))
        
            stats_overwrite_script = bytearray(b'')
            # Jump to code_cave
            stats_overwrite_script.extend(b'\xFF\x25\x00\x00\x00\x00')
            stats_overwrite_script.extend(stats_code_cave_address.to_bytes(8, byteorder="little"))
            stats_overwrite_script.extend(b'\x90\x90\x90\x90\x90\x90')
            pymem.memory.write_bytes(self.pm.process_handle, stats_opcode_address, bytes(stats_overwrite_script), len(stats_overwrite_script))
            print("Elden Ring Connection Ready")