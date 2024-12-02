const units = {
  '262144': {
    display: '',
  },
  '264864': {
    display: 'bpm',
  },
  '264928': {
    display: 'brpm',
  },
  '266560': {
     // display: 'F',   
     display: 'degF',  
     description: 'degree Fahrenheit',
  },
  '268192': {
    // display: 'C',
    display: 'Cel',
    description: 'degree Celsius',   
  },
  '264352': {
    display: 'minutes',
  },
  '266436': {
    display: 'mV',
  },
  '268768': {
    display: 'g-force',
  },
  '262688': {
    display: '%',
  },
  '266325': {
    display: 'pA',
  },
  '266016': {
    display: 'mmHg',
  }
};

tmp['MSH']['MSH.7']['MSH.7.1'] = DateUtil.getCurrentDate('yyyyMMddHHmmss');
tmp['MSH']['MSH.10']['MSH.10.1'] = UUIDGenerator.getUUID();


tmp['PID']['PID.3']['PID.3.1'] = msg['patient_primary_identifier'].toString();

tmp['OBR']['OBR.7']['OBR.7.1'] = msg['timestamp'].toString();
tmp['OBR']['OBR.10']['OBR.10.1'] = msg['device_primary_identifier'].toString();

tmp['OBX']['OBX.18']['OBX.18.1'] = msg['device_code'].toString();
tmp['OBX']['OBX.3']['OBX.3.1'] = msg['code'].toString();
tmp['OBX']['OBX.3']['OBX.3.3'] = "MDC";
tmp['OBX']['OBX.5']['OBX.5.1'] = msg['datapoints'].join("~");

if (units.hasOwnProperty(msg['unit_code'])) 
  {
    if(msg['unit_code'] != null && msg['unit_code'] != "" && units[msg['unit_code'].toString()].display != null && units[msg['unit_code'].toString()].display != "")
      {
        if(units[msg['unit_code'].toString()].display == 'degF' || units[msg['unit_code'].toString()].display == 'F')
        {
          tmp['OBX']['OBX.6']['OBX.6.1'] = units[msg['unit_code'].toString()].display;
          tmp['OBX']['OBX.6']['OBX.6.2'] = units[msg['unit_code'].toString()].description;
          tmp['OBX']['OBX.6']['OBX.6.3'] = "UCUM";
        }
        else if(units[msg['unit_code'].toString()].display == 'Cel' || units[msg['unit_code'].toString()].display == 'C')
        {
          tmp['OBX']['OBX.6']['OBX.6.1'] = units[msg['unit_code'].toString()].display;
          tmp['OBX']['OBX.6']['OBX.6.2'] = units[msg['unit_code'].toString()].description;
          tmp['OBX']['OBX.6']['OBX.6.3'] = "UCUM";
        }
        else
        { 
          tmp['OBX']['OBX.6']['OBX.6.1'] = units[msg['unit_code'].toString()].display;			
        }
    }
    else 
    {
          // Handle case where unit code is not found
          tmp['OBX']['OBX.6']['OBX.6.1'] = "";
    }
}