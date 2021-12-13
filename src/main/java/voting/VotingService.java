package voting;

import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class VotingService {
    @Cacheable("voting")
    public String getVoteNameByIsbn(String isbn){
        return findVoteInSlowSource(isbn);
    }

    private String findVoteInSlowSource(String isbn){
        try{
            Thread.sleep(3000);
        } catch (Exception e){
            e.printStackTrace();
        }
        return "Sample vote";
    }
}
