# pylint: disable=line-too-long
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch
from zipfile import ZipFile

from bod.models import BodDataset

from django.core.management import call_command


def xml_response(name):
    path = Path(__file__).parent / "data" / f"{name}.zip"
    with ZipFile(path, "r") as archive:
        xml = archive.read(archive.filelist[0])

    response = MagicMock()
    response.status_code = 200
    response.content = xml
    return response


def not_found_response():
    response = MagicMock()
    response.status_code = 404
    response.content = b""
    return response


@patch('distributions.management.commands.geocat_harvest.get')
@patch('distributions.management.commands.geocat_harvest.Session')
def test_command_harvests(dynamo_session_mock, requests_get_mock, db):
    requests_get_mock.side_effect = [
        xml_response("geocat_entry"), xml_response("geocat_thesaurus"), not_found_response()
    ]

    BodDataset.objects.create(
        id_dataset="ch.bafu.auen-vegetationskarten",
        fk_geocat="ab76361f-657d-4705-9053-95f89ecab126",
    )

    call_command("geocat_harvest", harvest_keywords=True, harvest_contacts=True, verbosity=2)

    # Note: These are the actual data in geocat at the time of writing this test, not parsing
    #       errors ;)

    assert dynamo_session_mock.mock_calls == [
        call(),
        call().client('dynamodb', region_name='eu-central-1'),
        call().client().put_item(
            TableName='harvest-keywords-dev',
            Item={
                'dataset_id': {
                    'S': 'ch.bafu.auen-vegetationskarten'
                },
                'geocat_id': {
                    'S': 'ab76361f-657d-4705-9053-95f89ecab126'
                },
                'keywords': {
                    'L': [
                        {
                            'M': {
                                'type': {
                                    'S': 'theme'
                                },
                                'thesaurus_id': {
                                    'S': 'geonetwork.thesaurus.local.theme.geocat.ch'
                                },
                                'thesaurus_url': {
                                    'S':
                                        'https://geocat-int.dev.bgdi.ch/geonetwork/srv/api/registries/vocabularies/local.theme.geocat.ch'
                                },
                                'thesaurus_date':
                                    {
                                        'S': '2024-06-13'
                                    },
                                'concept':
                                    {
                                        'S':
                                            'http://custom.shared.obj.ch/concept#948082ad-0adf-4d3c-8c4f-685f9d4d9372'
                                    },
                                'translation_de':
                                    {
                                        'S': 'e-geo.ch'
                                    },
                                'translation_fr':
                                    {
                                        'S': 'e-geo.ch'
                                    },
                                'translation_en':
                                    {
                                        'S': 'e-geo.ch'
                                    },
                                'translation_it':
                                    {
                                        'S': 'e-geo.ch'
                                    },
                                'translation_rm':
                                    {
                                        'NULL': True
                                    }
                            }
                        },
                        {
                            'M': {
                                'type': {
                                    'S': 'theme'
                                },
                                'thesaurus_id': {
                                    'S': 'geonetwork.thesaurus.local.theme.geocat.ch'
                                },
                                'thesaurus_url': {
                                    'S':
                                        'https://geocat-int.dev.bgdi.ch/geonetwork/srv/api/registries/vocabularies/local.theme.geocat.ch'
                                },
                                'thesaurus_date': {
                                    'S': '2024-06-13'
                                },
                                'concept': {
                                    'S':
                                        'http://custom.shared.obj.ch/concept#ae677a16-f81a-4533-9243-a87831115079'
                                },
                                'translation_de': {
                                    'S': 'BGDI Bundesgeodaten-Infrastruktur'
                                },
                                'translation_fr': {
                                    'S': 'IFDG l’Infrastructure Fédérale de données géographiques'
                                },
                                'translation_en': {
                                    'S': 'FSDI Federal Spatial Data Infrastructure'
                                },
                                'translation_it': {
                                    'S': 'IFDG Infrastruttura federale dei dati geografici'
                                },
                                'translation_rm': {
                                    'NULL': True
                                }
                            }
                        },
                        {
                            'M': {
                                'type': {
                                    'S': 'theme'
                                },
                                'thesaurus_id': {
                                    'S': 'geonetwork.thesaurus.local.theme.geocat.ch'
                                },
                                'thesaurus_url': {
                                    'S':
                                        'https://geocat-int.dev.bgdi.ch/geonetwork/srv/api/registries/vocabularies/local.theme.geocat.ch'
                                },
                                'thesaurus_date': {
                                    'S': '2024-06-13'
                                },
                                'concept': {
                                    'S':
                                        'http://geocat.ch/concept#94202915-c2c1-44fd-a106-71488110e399'
                                },
                                'translation_de': {
                                    'S': 'Aufbewahrungs- und Archivierungsplanung AAP - Bund'
                                },
                                'translation_fr': {
                                    'S':
                                        "Planification de la conservation et de l'archivage AAP - Conféderation"
                                },
                                'translation_en': {
                                    'S': 'Conservation and archiving planning AAP - Confederation'
                                },
                                'translation_it': {
                                    'S':
                                        'Pianificazione della conservazione e dell’archiviazione AAP - Confederazione'
                                },
                                'translation_rm': {
                                    'NULL': True
                                }
                            }
                        },
                        {
                            'M': {
                                'type': {
                                    'S': 'theme'
                                },
                                'thesaurus_id': {
                                    'S': 'geonetwork.thesaurus.local.theme.geocat.ch'
                                },
                                'thesaurus_url': {
                                    'S':
                                        'https://geocat-int.dev.bgdi.ch/geonetwork/srv/api/registries/vocabularies/local.theme.geocat.ch'
                                },
                                'thesaurus_date': {
                                    'S': '2024-06-13'
                                },
                                'concept': {
                                    'S':
                                        'http://geocat.ch/concept#e6485c01-fe69-485e-b194-035f682463db'
                                },
                                'translation_de': {
                                    'S': 'opendata.swiss'
                                },
                                'translation_fr': {
                                    'S': 'opendata.swiss'
                                },
                                'translation_en': {
                                    'S': 'opendata.swiss'
                                },
                                'translation_it': {
                                    'S': 'opendata.swiss'
                                },
                                'translation_rm': {
                                    'S': 'opendata.swiss'
                                }
                            }
                        }
                    ]
                }
            }
        ),
        call().client().put_item(
            TableName='harvest-contacts-dev',
            Item={
                'dataset_id': {
                    'S': 'ch.bafu.auen-vegetationskarten'
                },
                'geocat_id': {
                    'S': 'ab76361f-657d-4705-9053-95f89ecab126'
                },
                'contacts': {
                    'L': [{
                        'M': {
                            'role': {
                                'S': 'owner'
                            },
                            'org_name': {
                                'S': 'Bundesamt für Umwelt'
                            },
                            'org_name_de': {
                                'S': 'Bundesamt für Umwelt'
                            },
                            'org_name_fr': {
                                'S': "Office fédéral de l'environnement"
                            },
                            'org_name_en': {
                                'S': 'Federal Office for the Environment'
                            },
                            'org_name_it': {
                                'S': "Ufficio federale dell'ambiente"
                            },
                            'org_name_rm': {
                                'S': 'Bundesamt für Umwelt'
                            },
                            'org_acronym': {
                                'S': 'BAFU'
                            },
                            'org_acronym_de': {
                                'S': 'BAFU'
                            },
                            'org_acronym_fr': {
                                'S': 'BAFU'
                            },
                            'org_acronym_en': {
                                'S': 'BAFU'
                            },
                            'org_acronym_it': {
                                'S': 'BAFU'
                            },
                            'org_acronym_rm': {
                                'S': 'BAFU'
                            },
                            'org_email': {
                                'NULL': True
                            },
                            'position_name_de': {
                                'NULL': True
                            },
                            'position_name_fr': {
                                'NULL': True
                            },
                            'position_name_en': {
                                'NULL': True
                            },
                            'position_name_it': {
                                'NULL': True
                            },
                            'position_name_rm': {
                                'NULL': True
                            },
                            'individual_name': {
                                'NULL': True
                            },
                            'individual_first_name': {
                                'NULL': True
                            },
                            'individual_last_name': {
                                'NULL': True
                            },
                            'contact_direct_number': {
                                'NULL': True
                            },
                            'contact_voice': {
                                'S': '+41 58 462 93 11'
                            },
                            'contact_facsimile': {
                                'NULL': True
                            },
                            'contact_city': {
                                'S': 'Bern'
                            },
                            'contact_administrative_area': {
                                'NULL': True
                            },
                            'contact_postal_code': {
                                'S': '3003'
                            },
                            'contact_country': {
                                'NULL': True
                            },
                            'contact_electronic_mail_address': {
                                'S': 'info@bafu.admin.ch'
                            },
                            'contact_street_name': {
                                'NULL': True
                            },
                            'contact_street_number': {
                                'NULL': True
                            },
                            'contact_post_box': {
                                'NULL': True
                            },
                            'hours_of_service': {
                                'NULL': True
                            },
                            'contact_instructions': {
                                'NULL': True
                            },
                            'online_resources': {
                                'L': [{
                                    'M': {
                                        'url': {
                                            'NULL': True
                                        },
                                        'url_de': {
                                            'S': 'https://www.bafu.admin.ch/bafu/de/home.html'
                                        },
                                        'url_fr': {
                                            'S': 'https://www.bafu.admin.ch/bafu/fr/home.html'
                                        },
                                        'url_en': {
                                            'S': 'https://www.bafu.admin.ch/bafu/de/home.html'
                                        },
                                        'url_it': {
                                            'S': 'https://www.bafu.admin.ch/bafu/it/home.html'
                                        },
                                        'url_rm': {
                                            'S': 'https://www.bafu.admin.ch/bafu/en/home.html'
                                        },
                                        'protocol': {
                                            'S': 'WWW:LINK'
                                        },
                                        'name_de': {
                                            'NULL': True
                                        },
                                        'name_fr': {
                                            'NULL': True
                                        },
                                        'name_en': {
                                            'NULL': True
                                        },
                                        'name_it': {
                                            'NULL': True
                                        },
                                        'name_rm': {
                                            'NULL': True
                                        },
                                        'description_de': {
                                            'NULL': True
                                        },
                                        'description_fr': {
                                            'NULL': True
                                        },
                                        'description_en': {
                                            'NULL': True
                                        },
                                        'description_it': {
                                            'NULL': True
                                        },
                                        'description_rm': {
                                            'NULL': True
                                        }
                                    }
                                }]
                            }
                        }
                    },
                          {
                              'M': {
                                  'role': {
                                      'S': 'pointOfContact'
                                  },
                                  'org_name': {
                                      'S':
                                          'Bundesamt für Umwelt / Abteilung Biodiversität und '
                                          'Landschaft'
                                  },
                                  'org_name_de': {
                                      'S':
                                          'Bundesamt für Umwelt / Abteilung Biodiversität und '
                                          'Landschaft'
                                  },
                                  'org_name_fr': {
                                      'S':
                                          "Office fédéral de l'environnement / Division "
                                          "Biodiversité et paysage"
                                  },
                                  'org_name_en': {
                                      'S':
                                          'Federal Office for the Environment / Biodiversity '
                                          'and Landscape Division'
                                  },
                                  'org_name_it': {
                                      'S':
                                          "Ufficio federale dell'ambiente / Divisione "
                                          "Biodiversità e paesaggio"
                                  },
                                  'org_name_rm': {
                                      'S': 'Bundesamt für Umwelt'
                                  },
                                  'org_acronym': {
                                      'S': 'BAFU'
                                  },
                                  'org_acronym_de': {
                                      'S': 'BAFU'
                                  },
                                  'org_acronym_fr': {
                                      'S': 'OFEV'
                                  },
                                  'org_acronym_en': {
                                      'S': 'FOEN'
                                  },
                                  'org_acronym_it': {
                                      'S': 'UFAM'
                                  },
                                  'org_acronym_rm': {
                                      'S': 'BAFU'
                                  },
                                  'org_email': {
                                      'NULL': True
                                  },
                                  'position_name_de': {
                                      'NULL': True
                                  },
                                  'position_name_fr': {
                                      'NULL': True
                                  },
                                  'position_name_en': {
                                      'NULL': True
                                  },
                                  'position_name_it': {
                                      'NULL': True
                                  },
                                  'position_name_rm': {
                                      'NULL': True
                                  },
                                  'individual_name': {
                                      'NULL': True
                                  },
                                  'individual_first_name': {
                                      'NULL': True
                                  },
                                  'individual_last_name': {
                                      'S': 'BAFU BNL'
                                  },
                                  'contact_direct_number': {
                                      'NULL': True
                                  },
                                  'contact_voice': {
                                      'S': '+41 58 462 93 89'
                                  },
                                  'contact_facsimile': {
                                      'S': '+41 58 463 89 74'
                                  },
                                  'contact_city': {
                                      'S': 'Bern'
                                  },
                                  'contact_administrative_area': {
                                      'NULL': True
                                  },
                                  'contact_postal_code': {
                                      'S': '3003'
                                  },
                                  'contact_country': {
                                      'S': 'CH'
                                  },
                                  'contact_electronic_mail_address': {
                                      'S': 'bnl@bafu.admin.ch'
                                  },
                                  'contact_street_name': {
                                      'NULL': True
                                  },
                                  'contact_street_number': {
                                      'NULL': True
                                  },
                                  'contact_post_box': {
                                      'NULL': True
                                  },
                                  'hours_of_service': {
                                      'NULL': True
                                  },
                                  'contact_instructions': {
                                      'NULL': True
                                  },
                                  'online_resources': {
                                      'L': [{
                                          'M': {
                                              'url': {
                                                  'NULL': True
                                              },
                                              'url_de': {
                                                  'S':
                                                      'https://www.bafu.admin.ch/bafu/de/home/amt/abteilungen-sektionen/abteilung-biodiversitaet-und-landschaft.html'
                                              },
                                              'url_fr': {
                                                  'S':
                                                      'https://www.bafu.admin.ch/bafu/fr/home/office/divisions-sections/division-biodiversite-et-paysage.html'
                                              },
                                              'url_en': {
                                                  'S':
                                                      'https://www.bafu.admin.ch/bafu/en/home/office/divisions-sections/biodiversity-and-landscape-division.html'
                                              },
                                              'url_it': {
                                                  'S':
                                                      'https://www.bafu.admin.ch/bafu/it/home/ufficio/divisioni-sezioni/divisione-biodiversita-e-paesaggio.html'
                                              },
                                              'url_rm': {
                                                  'NULL': True
                                              },
                                              'protocol': {
                                                  'S': 'WWW:LINK'
                                              },
                                              'name_de': {
                                                  'NULL': True
                                              },
                                              'name_fr': {
                                                  'NULL': True
                                              },
                                              'name_en': {
                                                  'NULL': True
                                              },
                                              'name_it': {
                                                  'NULL': True
                                              },
                                              'name_rm': {
                                                  'NULL': True
                                              },
                                              'description_de': {
                                                  'NULL': True
                                              },
                                              'description_fr': {
                                                  'NULL': True
                                              },
                                              'description_en': {
                                                  'NULL': True
                                              },
                                              'description_it': {
                                                  'NULL': True
                                              },
                                              'description_rm': {
                                                  'NULL': True
                                              }
                                          }
                                      }]
                                  }
                              }
                          }]
                }
            }
        )
    ]
