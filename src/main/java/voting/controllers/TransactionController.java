package voting.controllers;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import voting.Block;
import voting.BlockChain;
import voting.Transaction;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@RestController
public class TransactionController {

    @GetMapping("/transactions")
    public List<Transaction> all(){
        System.out.println("Getting transactions...");
        List<Transaction> transactions = new ArrayList<>();
        for (var block:
                BlockChain.blockchain) {
            for (var transaction:
                    block.transactions) {
                if (transaction.inputs != null) {
                    transactions.add(transaction);
                }
            }
        }

        return transactions;
    }
}
