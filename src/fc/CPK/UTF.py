from struct import unpack
READFLOAT = lambda b: unpack('f', b)

ENDIAN = "big"
UTFCODE = b"@UTF"
ENCODING = "shift_jis"
MAX_COLUMN_NAME = 255



STORAGE_MASK = 0xf0
STORAGE_NONE = 0x00
STORAGE_ZERO = 0x10
STORAGE_CONSTANT = 0x30
STORAGE_PERROW = 0x50

TYPE_MASK = 0x0f
TYPE_DATA = 0x0b
TYPE_STRING = 0x0a
TYPE_FLOAT = 0x08
TYPE_8BYTE2 = 0x07
TYPE_8BYTE = 0x06
TYPE_4BYTE2 = 0x05
TYPE_4BYTE = 0x04
TYPE_2BYTE2 = 0x03
TYPE_2BYTE = 0x02
TYPE_1BYTE2 = 0x01
TYPE_1BYTE = 0x00

class UTF():
    
    def __init__(self, utf_packet):
        
        offset = 0
        
        self.size = len(utf_packet)
        
        if utf_packet[offset:offset+4] != UTFCODE:
            raise Exception(f"{utf_packet[offset:offset+4]} get instead of {UTFCODE}, problem with decryptUTF or your UTF datas are corrupt")
        offset += 4 #4
            
        self.table_size = int.from_bytes(utf_packet[offset:offset+4], ENDIAN)
        offset += 4 #8
        
        self.rows_offset = int.from_bytes(utf_packet[offset:offset+4], ENDIAN)
        offset += 4 #12
        
        self.strings_offset = int.from_bytes(utf_packet[offset:offset+4], ENDIAN)
        offset += 4 #16
        
        self.data_offset = int.from_bytes(utf_packet[offset:offset+4], ENDIAN)
        offset += 4 #20
        
        # Osef CPK Header & UTF Header, so +8 for each self.XXX_offset
        self.rows_offset += 8
        self.strings_offset += 8
        self.data_offset += 8
        
        self.table_name = int.from_bytes(utf_packet[offset:offset+4], ENDIAN)
        offset += 4 #24
        
        self.nb_columns = int.from_bytes(utf_packet[offset:offset+2], ENDIAN)
        offset += 2 #26
        
        self.row_lenght = int.from_bytes(utf_packet[offset:offset+2], ENDIAN)
        offset += 2 #28
        
        self.nb_rows = int.from_bytes(utf_packet[offset:offset+4], ENDIAN)
        offset += 4 #32
        
        # read columns
        self.columns = []
        
        for _ in range(self.nb_columns):
            flags = utf_packet[offset]
            offset += 1
            if flags == 0:
                flags = utf_packet[offset+3]
                offset += 4
            
            column_offset = int.from_bytes(utf_packet[offset:offset+4], ENDIAN) + self.strings_offset
            offset += 4
            name_ba = bytearray()
            for _ in range(MAX_COLUMN_NAME):
                char = utf_packet[column_offset]
                column_offset += 1
                if char == 0:
                    break
                name_ba.append(char)
            name = name_ba.decode(ENCODING)
            
            self.columns.append(COLUMN(flags, name))
            
        # read rows
        self.rows = []
        
        for j in range(self.nb_rows):
            
            current_offset = self.rows_offset + j*self.row_lenght
            current_rows = []
            
            for i in range(self.nb_columns):
                
                storage_flag = self.columns[i].flags & STORAGE_MASK
                
                if storage_flag == STORAGE_NONE: #0x00
                    current_rows.append(ROW())
                    continue
                if storage_flag == STORAGE_ZERO: #0x10
                    current_rows.append(ROW())
                    continue
                if storage_flag == STORAGE_CONSTANT: #0x30
                    current_rows.append(ROW())
                    continue
                
                #0x50
                row_type = self.columns[i].flags & TYPE_MASK
                row_position = current_offset
                row_data = None
                
                match row_type:
                    case 0x0 | 0x1:
                        row_data = int.from_bytes(utf_packet[current_offset:current_offset+1], ENDIAN)
                        current_offset += 1
                    case 0x2 | 0x3:
                        row_data = int.from_bytes(utf_packet[current_offset:current_offset+2], ENDIAN)
                        current_offset += 2
                    case 0x4 | 0x5:
                        row_data = int.from_bytes(utf_packet[current_offset:current_offset+4], ENDIAN)
                        current_offset += 4
                    case 0x6 | 0x7:
                        row_data = int.from_bytes(utf_packet[current_offset:current_offset+8], ENDIAN)
                        current_offset += 8
                    case 0x8:
                        row_data = READFLOAT(utf_packet[current_offset:current_offset+4])
                        current_offset += 4
                    case 0xa:
                        row_offset = int.from_bytes(utf_packet[current_offset:current_offset+4], ENDIAN) + self.strings_offset
                        data_ba = bytearray()
                        for _ in range(MAX_COLUMN_NAME):
                            char = utf_packet[row_offset]
                            row_offset += 1
                            current_offset += 1
                            if char == 0:
                                break
                            data_ba.append(char)
                            row_data = data_ba.decode(ENCODING)
                    case 0xb:
                        row_position = int.from_bytes(utf_packet[current_offset:current_offset+4], ENDIAN) + self.data_offset
                        size = int.from_bytes(utf_packet[current_offset+4:current_offset+8], ENDIAN)
                        current_offset += 8
                        row_data = utf_packet[row_position: row_position+size]
                    case _:
                        raise Exception(f"Type of row cannot be {hex(row_type)}")
                        
                current_rows.append(ROW(row_type, row_position, row_data))
            
            self.rows.append(current_rows)
    
    def get_Column_Data(self, row, Name):
        
        for i in range(self.nb_columns):
            if self.columns[i].name == Name:
                return self.rows[row][i].data
            
        return None

    def get_Column_Data2(self, row, Name, type):
        
        temp = self.get_Column_Data(row, Name)
        
        if temp is None:
            
            match type:
                case 0:
                    return 0xff
                case 1:
                    return 0xffff
                case 2:
                    return 0xffffffff
                case 3:
                    return 0xffffffffffffffff
                
            temp_type = self.get_Column_Type(row, Name)
            match temp_type:
                case 1 | 2:
                    return 0xffff
                case 3 | 4:
                    return 0xffffffff
                case 5 | 6:
                    return 0xffffffffffffffff
                
            return 0
        return temp
    
    def get_Column_Position(self, row, Name):
        
        for i in range(self.nb_columns):
            if self.columns[i].name == Name:
                return self.rows[row][i].position
            
        return -1
    
    def get_Column_Type(self, row, Name):
        
        for i in range(self.nb_columns):
            if self.columns[i].name == Name:
                return self.rows[row][i].type
            
        return -1
            
    def print_data(self, size_space = 15):
        
        DATA = [
            ("Size", self.size),
            ("Table size", self.table_size),
            ("Rows offset", self.rows_offset),
            ("Strings offset", self.strings_offset),
            ("Data offset", self.data_offset),
            ("Table name", self.table_name),
            ("Number columns", self.nb_columns),
            ("Row lenght", self.row_lenght),
            ("Number rows", self.nb_rows)
            ]
        
        for data in DATA:
            print(data[0] + ":" + " "*(size_space-len(data[0])), hex(data[1]))
            
        self.print_data_column()
        
        self.print_data_row()
            
    def print_data_column(self):
            
        for column in self.columns:
            column.print_data()
            
    def print_data_row(self):
        
        for rows in self.rows:
            for row in rows:
                row.print_data()
            
class COLUMN():
    
    def __init__(self, flags, name):
        
        self.flags = flags
        self.name = name
        
    def print_data(self):
        print("COLUMN: flags:", hex(self.flags), "name:", self.name)
        
class ROW():
    
    """
    data type depending of type:
    0x0 or 0x1: uint8
    0x2 or 0x3: uint16
    0x4 or 0x5: uint32
    0x6 or 0x7: uint64
    0x8: ufloat
    0xA: string
    0xB: bytes
    """
    
    def __init__(self, type = -1, position = -1, data = None):
        self.type = type
        self.position = position
        self.data = data
        
    def print_data(self):
        print("ROW: type:", hex(self.type), "position:", hex(self.position), "data:", self.data)