import React, {Component} from 'react';
import AthleteCard from './AthleteCard';
// import NewathleteModal from "./NewathleteModal";
// import ConfirmRemovalModal from "./ConfirmRemovalModal";

class AthleteList extends Component {
  render() {
    const athletes = this.props.athletes;
    return (
      <div>
        {!athletes || athletes.length <= 0 ? (
                <b>No athletes found</b>
          ) : (
            athletes.map((athlete) => (
              <AthleteCard athlete={athlete} key={athlete.pk}/>

            ))
          )}
      </div>
    );
  }
}

export default AthleteList;
