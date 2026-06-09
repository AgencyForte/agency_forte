
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://sgrzyhwoeggudwqxnooz.supabase.co',
  'sb_publishable_WxelCIjACLdkJipZAPXtWQ_pjJBHwmT'
);

async function run() {
  console.log('Inserting matrices...');
  await supabase.from('carrier_to_line_matrix').upsert([
    { carrier_naic: '10052', carrier_name: 'Chubb', line_of_business: 'Property and Casualty' },
    { carrier_naic: '25674', carrier_name: 'Travelers', line_of_business: 'Property and Casualty' },
    { carrier_naic: '24082', carrier_name: 'Ohio Security', line_of_business: 'Property and Casualty' },
    { carrier_naic: '10999', carrier_name: 'Progressive Commercial', line_of_business: 'Commercial Auto' }
  ], { onConflict: 'carrier_naic,line_of_business' });

  console.log('Inserting buyer appointments...');
  await supabase.from('master_agency_appointments').upsert([
    { agency_tdi_id: 'npn:123456', carrier_naic: '10052', carrier_name: 'Chubb', is_active: true, structural_hash: 'seed_buy1' },
    { agency_tdi_id: 'npn:654321', carrier_naic: '10999', carrier_name: 'Progressive Commercial', is_active: true, structural_hash: 'seed_buy2' }
  ], { onConflict: 'agency_tdi_id,carrier_naic,appointment_type' });

  console.log('Done mapping.');
}

run();

