import logging
import forta_agent
import re
import pandas as pd
from forta_agent import EntityType


class BaseBotParser:

    BASEBOT_PARSING_CONFIG_DF = pd.read_csv('basebot_parsing_config.csv')

    @staticmethod
    def get_scammer_addresses(w3, alert_event: forta_agent.alert_event.AlertEvent) -> dict:
        scammer_addresses = dict()
       
                    
        for index, row in BaseBotParser.BASEBOT_PARSING_CONFIG_DF.iterrows():
            #  bot_id,alert_id,location,attacker_address_location_in_description,metadata_field,address_information
            #  address information is to further differentiate one type of address vs the other from the same bot alert (e.g. address-poisioning vs address-posioner)

            #  contract address is also parsed where applicable and added as 'scammer-contracts' set in the metadata 

            if row['bot_id'] == alert_event.bot_id and row['alert_id'] in alert_event.alert_id and row["type"] == 'eoa':
                if row['location'] == 'description':
                    metadata_obj = alert_event.alert.metadata.copy()
                    description = alert_event.alert.description.lower()
                    loc = int(row["attacker_address_location_in_description"])
                    metadata_obj["address_information"] = row["address_information"]
                    metadata_obj["scammer-contracts"] = BaseBotParser.get_scammer_contract_addresses(w3, alert_event)
                    scammer_addresses[description[loc:42+loc]] = metadata_obj

                elif row['location'] == 'metadata':
                    if row['metadata_field'] in alert_event.alert.metadata.keys():
                        metadata_obj = alert_event.alert.metadata.copy()
                        metadata = metadata_obj[row["metadata_field"]]
                        for address in re.findall(r"0x[a-fA-F0-9]{40}", metadata):
                            metadata_obj["address_information"] = row["address_information"]
                            metadata_obj["scammer-contracts"] = BaseBotParser.get_scammer_contract_addresses(w3, alert_event)
                            scammer_addresses[address.lower()] = metadata_obj
                elif row['location'] == 'tx_to':
                    metadata_obj = alert_event.alert.metadata.copy()
                    metadata_obj["address_information"] = row["address_information"]
                    metadata_obj["scammer-contracts"] = BaseBotParser.get_scammer_contract_addresses(w3, alert_event)
                    scammer_addresses[w3.eth.get_transaction(alert_event.transaction_hash)['to'].lower()] = metadata_obj
            
        return scammer_addresses
    
    @staticmethod
    def get_scammer_contract_addresses(w3, alert_event: forta_agent.alert_event.AlertEvent) -> set:
        scammer_contract_addresses = set()

        for index, row in BaseBotParser.BASEBOT_PARSING_CONFIG_DF.iterrows():
            if row['bot_id'] == alert_event.bot_id and row['alert_id'] in alert_event.alert_id and row["type"] == 'contract':
                if row['location'] == 'description':
                    metadata_obj = alert_event.alert.metadata.copy()
                    description = alert_event.alert.description.lower()
                    loc = int(row["attacker_address_location_in_description"])
                    scammer_contract_addresses.add(description[loc:42+loc])
                elif row['location'] == 'metadata':
                    if row['metadata_field'] in alert_event.alert.metadata.keys():
                        metadata_obj = alert_event.alert.metadata.copy()
                        metadata = metadata_obj[row["metadata_field"]]
                        for address in re.findall(r"0x[a-fA-F0-9]{40}", metadata):
                            scammer_contract_addresses.add(address.lower())
                elif row['location'] == 'tx_to':
                    metadata_obj = alert_event.alert.metadata.copy()
                    scammer_contract_addresses.add(w3.eth.get_transaction(alert_event.transaction_hash)['to'].lower())

        return scammer_contract_addresses
