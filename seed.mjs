
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://sgrzyhwoeggudwqxnooz.supabase.co',
  'sb_publishable_WxelCIjACLdkJipZAPXtWQ_pjJBHwmT'
);

async function run() {
  console.log('Clearing old mock events...');
  await supabase.from('market_timeline').delete().neq('event_id', '00000000-0000-0000-0000-000000000000');

  console.log('Inserting master records...');
  await supabase.from('master_agencies').upsert([
    { agency_tdi_id: 'npn:123456', name: 'Austin Premier Insurance Group' },
    { agency_tdi_id: 'npn:654321', name: 'Dallas Elite Risk Partners' }
  ]);
  await supabase.from('master_agents').upsert([
    { agent_npn: '987654', full_name: 'Johnathan Doe' },
    { agent_npn: '112233', full_name: 'Sarah Smith' }
  ]);

  console.log('Inserting enriched test events...');
  const { error } = await supabase.from('market_timeline').insert([
    {
      event_type: 'COMPETITOR_BLEEDING',
      target_agency_id: 'npn:123456',
      target_agent_npn: '987654',
      event_zip: '78701',
      event_county: 'Travis',
      confidence: 'high',
      event_fingerprint: 'test-bleed-1',
      payload: {
        source_rule: '36_month_tenure_filter',
        agency_name: 'Austin Premier Insurance Group',
        agent_name: 'Johnathan Doe',
        tenure_months: 41,
        association_type: 'Sub-Agent',
        departing_carriers: [
          { carrier_naic: '10052', carrier_name: 'Chubb National Ins Co', line_of_business: 'Property and Casualty' },
          { carrier_naic: '25674', carrier_name: 'Travelers Property Cas Co Of Amer', line_of_business: 'Property and Casualty' }
        ]
      }
    },
    {
      event_type: 'LOB_ENCROACHMENT',
      target_agency_id: 'npn:654321',
      target_agent_npn: '112233',
      event_zip: '75201',
      event_county: 'Dallas',
      confidence: 'high',
      event_fingerprint: 'test-lob-1',
      payload: {
        source_rule: 'veteran_hire_overlap',
        agency_name: 'Dallas Elite Risk Partners',
        agent_name: 'Sarah Smith',
        tenure_months: 64,
        lines_overlapped: ['Property and Casualty', 'Commercial Auto'],
        historical_carriers: [
          { carrier_naic: '24082', carrier_name: 'Ohio Security Ins Co', line_of_business: 'Property and Casualty' },
          { carrier_naic: '10999', carrier_name: 'Progressive Commercial', line_of_business: 'Commercial Auto' }
        ]
      }
    }
  ]);
  
  if (error) console.error(error);
  else console.log('Successfully seeded enriched events.');
}

run();

