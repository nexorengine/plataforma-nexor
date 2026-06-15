const CATALOG = {
  cirurgia_geral: {
    label: 'Cirurgia Geral',
    code: 'CG',
    icon: 'ti-cut',
    dominios: [
      { slug: 'abdome_agudo',                               code: 'CG_D01', nome: 'Abdome Agudo' },
      { slug: 'hepatobiliar_pancreas',                      code: 'CG_D02', nome: 'Hepatobiliar e Pâncreas' },
      { slug: 'trauma_urgencia',                            code: 'CG_D03', nome: 'Trauma e Urgência Cirúrgica' },
      { slug: 'perioperatorio',                             code: 'CG_D04', nome: 'Perioperatório' },
      { slug: 'hernias_parede_abdominal',                   code: 'CG_D05', nome: 'Hérnias e Parede Abdominal' },
      { slug: 'trato_digestivo_superior',                   code: 'CG_D06', nome: 'Trato Digestivo Superior' },
      { slug: 'trato_digestivo_inferior_coloproctologia',   code: 'CG_D07', nome: 'Trato Digestivo Inferior e Coloproctologia' },
      { slug: 'cirurgia_vascular',                          code: 'CG_D08', nome: 'Cirurgia Vascular' },
      { slug: 'queimaduras',                                code: 'CG_D09', nome: 'Queimaduras' },
    ]
  },
  gineco_obstetricia: {
    label: 'Ginecologia & Obstetrícia',
    code: 'GO',
    icon: 'ti-baby-carriage',
    dominios: [
      { slug: 'pre_natal',                    code: 'GO_D01', nome: 'Pré-Natal' },
      { slug: 'parto_normal',                 code: 'GO_D02', nome: 'Parto Normal' },
      { slug: 'puerperio_aleitamento',        code: 'GO_D03', nome: 'Puerpério e Aleitamento' },
      { slug: 'complicacoes_obstetricas',     code: 'GO_D04', nome: 'Complicações Obstétricas' },
      { slug: 'ginecologia_geral',            code: 'GO_D05', nome: 'Ginecologia Geral' },
      { slug: 'doencas_uterinas_anexiais',    code: 'GO_D06', nome: 'Doenças Uterinas e Anexiais' },
      { slug: 'infeccoes_genitais_dsts',      code: 'GO_D07', nome: 'Infecções Genitais e DSTs' },
      { slug: 'cancer_ginecologico',          code: 'GO_D08', nome: 'Câncer Ginecológico' },
      { slug: 'uroginecologia_piso_pelvico',  code: 'GO_D09', nome: 'Uroginecologia e Piso Pélvico' },
    ]
  },
  clinica_medica: {
    label: 'Clínica Médica',
    code: 'CM',
    icon: 'ti-heart-rate-monitor',
    dominios: [
      { slug: 'cardiologia',      code: 'CM_D01', nome: 'Cardiologia' },
      { slug: 'pneumologia',      code: 'CM_D02', nome: 'Pneumologia' },
      { slug: 'gastroenterologia',code: 'CM_D03', nome: 'Gastroenterologia' },
      { slug: 'nefrologia',       code: 'CM_D04', nome: 'Nefrologia' },
      { slug: 'endocrinologia',   code: 'CM_D05', nome: 'Endocrinologia' },
      { slug: 'hematologia',      code: 'CM_D06', nome: 'Hematologia' },
      { slug: 'reumatologia',     code: 'CM_D07', nome: 'Reumatologia' },
      { slug: 'infectologia',     code: 'CM_D08', nome: 'Infectologia' },
      { slug: 'neurologia',       code: 'CM_D09', nome: 'Neurologia' },
    ]
  },
  pediatria: {
    label: 'Pediatria',
    code: 'PED',
    icon: 'ti-baby',
    dominios: [
      { slug: 'neonatologia',         code: 'PED_D01', nome: 'Neonatologia' },
      { slug: 'puericultura',         code: 'PED_D02', nome: 'Puericultura' },
      { slug: 'pneumologia_ped',      code: 'PED_D03', nome: 'Pneumologia Pediátrica' },
      { slug: 'gastro_ped',           code: 'PED_D04', nome: 'Gastroenterologia Pediátrica' },
      { slug: 'infectologia_ped',     code: 'PED_D05', nome: 'Infectologia Pediátrica' },
      { slug: 'cardio_ped',           code: 'PED_D06', nome: 'Cardiologia Pediátrica' },
      { slug: 'endocrinologia_ped',   code: 'PED_D07', nome: 'Endocrinologia Pediátrica' },
      { slug: 'hematologia_onco_ped', code: 'PED_D08', nome: 'Hematologia e Oncologia Pediátrica' },
      { slug: 'emergencias_ped',      code: 'PED_D09', nome: 'Emergências Pediátricas' },
    ]
  },
  medicina_preventiva: {
    label: 'Medicina Preventiva',
    code: 'PREV',
    icon: 'ti-shield-check',
    dominios: [
      { slug: 'epidemiologia_geral',          code: 'PREV_D01', nome: 'Epidemiologia Geral' },
      { slug: 'vigilancia_epidemiologica',    code: 'PREV_D02', nome: 'Vigilância Epidemiológica' },
      { slug: 'imunizacao_pni',               code: 'PREV_D03', nome: 'Imunização e PNI' },
      { slug: 'bioestatistica',               code: 'PREV_D04', nome: 'Bioestatística' },
      { slug: 'saude_familia_aps',            code: 'PREV_D05', nome: 'Saúde da Família e APS' },
      { slug: 'politica_nacional_sus',        code: 'PREV_D06', nome: 'Política Nacional de Saúde e SUS' },
      { slug: 'saude_ambiental_ocupacional',  code: 'PREV_D07', nome: 'Saúde Ambiental e Ocupacional' },
      { slug: 'dcnt_promocao_saude',          code: 'PREV_D08', nome: 'DCNT e Promoção da Saúde' },
      { slug: 'bioetica_etica_medica',        code: 'PREV_D09', nome: 'Bioética e Ética Médica' },
    ]
  }
};

const AREA_ORDER = ['cirurgia_geral','gineco_obstetricia','clinica_medica','pediatria','medicina_preventiva'];
