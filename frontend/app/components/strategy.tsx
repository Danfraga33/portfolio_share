import Rules from "./rules";
import Big_TA from "./big_ta";

const Strategy = () => {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col justify-evenly gap-6 p-4 lg:flex-row">
      {/* Rules Component */}
      <div className="w-full flex-1 lg:w-1/2">
        <Rules />
      </div>

      {/* Big_TA Component */}
      <div className="w-full flex-1 lg:w-1/2">
        <Big_TA />
      </div>
    </div>
  );
};

export default Strategy;
