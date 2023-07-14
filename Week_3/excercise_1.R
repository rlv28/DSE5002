two_sum_shorter <- function(nums_vector,target){
  # a function to find the indices of two values in a vector that sum to target. This version of the function works to only 
  #each possible pair of indices once. 
  
  loop_work <- 0
  
  if(is.numeric(nums_vector)&is.numeric(target)){             #Check that all values are numeric
    for(i in 1:(length(nums_vector)-1)) {                                            
      for(j in (i+1):length(nums_vector)) {                                          
        loop_work <- loop_work + 1
       
        if ((nums_vector[i] + nums_vector[j]) == target){
          cat(i, j)
          cat ('\n')
        }
        
      }
    }
  } else{
    stop("ERROR: All values in the vector and the target must be numeric.")
  }
  
  return(loop_work)  
}




# Test code
nums_vector <- c(5,7,12,34,6,10,8,9)
target <- 13

two_sum_shorter(nums_vector,target)
#expected answers
#[1] 1 7
#[1] 2 5
#[1] 5 2

