package voting.controllers;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import voting.VotingService;

@RestController
@RequestMapping("/voting")
public class VotingController {
    @Autowired
    private VotingService votingService;

    @GetMapping("/{isbn}")
    public String getVoteByName(@PathVariable("isbn") String isbn){
        return votingService.getVoteNameByIsbn(isbn);
    }
}
