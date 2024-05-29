# Unverified Contract Creation Agent

## Description

This agent alerts when a new contract is created with unverified source code as per Etherscan.

## Supported Chains

- All EVM compatible chains; if tracing is supported, the bot is able to check contract creations by contracts

## Alerts

Describe each of the type of alerts fired by this agent

- UNVERIFIED-CODE-CONTRACT-CREATION
  - Fires when a contract is created but blockchain explorer has no verified code for the contract
  - Severity is always set to "medium"
  - Type is always set to "suspicious"
  - Low confidence labels (0.3) for attacker address and attacker_contract address are emitted
  - Metadata exposes the anomaly_score for the alert (calculated by dividing unverified contract creations by all contract creations)

## Test Data

The agent behaviour can be verified with the following transactions:

- 0x531e42376038809d98fd488edddb33126431bda870bd3f43984025486a3f4f68 (Fei Rari attacker contract)
- 0x16718a6df144de749035e4763946ad56d3dfaeb5d151a82f913698fa4ae28c3d (Conic Finance Exploiter contract)

## Running Locally

To run the project locally, follow these steps:

### Prerequisites

- **Node.js**: Ensure you have the version specified in the `.nvmrc` file installed. You can use `nvm` (Node Version Manager) to manage Node.js versions.

  ```sh
  nvm install
  nvm use
  ```

- **Python 3.10**: Make sure you have Python 3.10 installed. You can create a virtual environment for Python 3.10.

  ```sh
  python3.10 -m venv venv
  source venv/bin/activate
  ```

- **Secrets**: Fill out the `secrets.example.json` file and rename it to `secrets.json`. This file should contain the necessary API keys for the project to function.

  ```json
  {
      "apiKeys": {
          "ETHERSCAN_TOKEN": "your_actual_etherscan_api_key",
          "POLYGONSCAN_TOKEN": "your_actual_polygonscan_api_key",
          "BSCSCAN_TOKEN": "your_actual_bscscan_api_key",
          "ARBISCAN_TOKEN": "your_actual_arbiscan_api_key",
          "OPTIMISTICSCAN_TOKEN": "your_actual_optimisticscan_api_key",
          "FTMSCAN_TOKEN": "your_actual_ftmscan_api_key",
          "SNOWTRACE_TOKEN": "your_actual_snowtrace_api_key"
      }
  }
  ```

### Installation

1. **Clone the repository**:

    ```sh
    git clone git@github.com:zenchain-protocol/forta-network-starter-kits-bots.git
    cd unverified-contract-py
    ```

2. **Install Node.js (and Python) dependencies**:

    ```sh
    npm install
    ```


### Running the Application

You can run the application in different modes:

- **Development Mode**: This mode watches for changes in the source code and restarts the application automatically.

  ```sh
  npm run start:dev
  ```

- **Production Mode**: This mode runs the application in a production environment.

  ```sh
  npm run start:prod
  ```

- **Transaction Mode**: This mode runs the application on a specific transaction.

  ```sh
  npm run tx 0x531e42376038809d98fd488edddb33126431bda870bd3f43984025486a3f4f68
  ```

- **Block Mode**: This mode runs the application on a specific block.

  ```sh
  npm run block 123
  ```

- **Range Mode**: This mode runs the application with on a range of blocks.

  ```sh
  npm run range
  ```

- **File Mode**: This mode runs the application with data from a file.

  ```sh
  npm run file
  ```

### Running with Docker

Alternatively, you can run the application using Docker. Make sure you have Docker installed on your machine.

1. **Build the Docker image**:

    ```sh
    docker build -t unverified-contract-creation .
    ```

2. **Run the Docker container**:

    ```sh
    docker run -d unverified-contract-creation
    ```

### Testing

You can run the tests using the following command:

```sh
npm test
```

### Publishing

To publish the Forta agent:

```sh
npm run publish
```

### Additional Commands

- **Push the Forta agent**:

  ```sh
  npm run push
  ```

- **Disable the Forta agent**:

  ```sh
  npm run disable
  ```

- **Enable the Forta agent**:

  ```sh
  npm run enable
  ```

- **Generate a keyfile for the Forta agent**:

  ```sh
  npm run keyfile
  ```

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.