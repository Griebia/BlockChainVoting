package voting;

import org.web3j.crypto.Bip39Wallet;
import org.web3j.crypto.Credentials;
import org.web3j.crypto.ECKeyPair;
import org.web3j.crypto.WalletUtils;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameterName;
import org.web3j.protocol.core.methods.response.EthGasPrice;
import org.web3j.protocol.core.methods.response.EthGetBalance;
import org.web3j.protocol.core.methods.response.Web3ClientVersion;
import org.web3j.protocol.http.HttpService;
import org.web3j.utils.Convert;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.concurrent.ExecutionException;

public class EthereumConnection {
    public static void main(String[] args) {
        System.out.println("Connecting to the ethereum node");
        Web3j web3 = Web3j.build(new HttpService("HTTP://127.0.0.1:7545"));
        System.out.println("Successfully connected to the node");
        try {
            Web3ClientVersion clientVersion = web3.web3ClientVersion().send();
            System.out.println("Client version: " + clientVersion.getWeb3ClientVersion());
            EthGasPrice gasPrice = web3.ethGasPrice().send();
            System.out.println("Default Gas Price: " + gasPrice.getGasPrice());
            EthGetBalance ethGetBalance = web3
                    .ethGetBalance("0xcF8B652b0173FBABE734f5F388C2da24a2359993", DefaultBlockParameterName.LATEST)
                    .sendAsync().get();
            System.out.println("Balance: of Account ‘0xcF8B652b0173FBABE734f5F388C2da24a2359993’"
                    + ethGetBalance.getBalance());

            System.out.println("Balance in Ether format: "
                    + Convert.fromWei(web3.ethGetBalance("0xcF8B652b0173FBABE734f5F388C2da24a2359993",
                    DefaultBlockParameterName.LATEST).send().getBalance().toString(), Convert.Unit.ETHER));

            web3
        } catch (IOException ex) {
            throw new RuntimeException("Error whilst sending json-rpc requests", ex);
        } catch (ExecutionException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        createWallet();
    }


    public static void createWallet() {
        try {
            System.out.println("Creating New Account");
            BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
            System.out.println("Enter New Password");
            String walletPassword = br.readLine();
            /* Define Wallet File Location */
            String location = System.getProperty("user.dir") + "/tmp/";
            File walletDirectory = new File(location);
            Bip39Wallet walletName = WalletUtils.generateBip39Wallet(walletPassword, walletDirectory);
            System.out.println("wallet location: " + walletDirectory + "/" + walletName);
            Credentials credentials = WalletUtils.loadBip39Credentials(walletPassword, walletName.getMnemonic());
            String accountAddress = credentials.getAddress();
            System.out.println("Account address: " + credentials.getAddress());
            ECKeyPair privateKey = credentials.getEcKeyPair();
            String seedPhrase = walletName.getMnemonic();
            System.out.println("Account Details:");
            System.out.println("Your New Account : " + credentials.getAddress());
            System.out.println("Mneminic Code: " + walletName.getMnemonic());
            System.out.println("Private Key: " + privateKey.getPrivateKey().toString(16));
            System.out.println("Public Key: " + privateKey.getPublicKey().toString(16));
        } catch (Exception e) {
            e.printStackTrace();
        }

    }
}